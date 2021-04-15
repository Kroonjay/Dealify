import asyncio
import logging
from datetime import datetime
from itertools import cycle
from typing import List
from time import perf_counter

from core.tasks.executor import run_dealify_task
from core.database.db_helpers import start_pool, run_sproc, read_model, list_from_rows
from core.database.sprocs import update_dealify_worker_status_sproc, read_dealify_worker_by_id_sproc, read_dealify_task_ids_by_type_sproc, read_dealify_task_by_id_sproc
from core.configs.config import DEALIFY_DB_CREDS
from core.enums.statuses import DealifyWorkerStatus
from core.models.dealify.dealify_worker import DealifyWorkerModel
from core.models.dealify.dealify_task import DealifyTask
from worker.config import WORKER_ID, WORKER_LOG_LEVEL, WORKER_LOG_FILE, WORKER_LOG_FORMAT, BASE_LOGGER_NAME


def start_logger(log_level=WORKER_LOG_LEVEL):
    logging.basicConfig(level=log_level,
                        filename=WORKER_LOG_FILE,
                        filemode='w')
    root_logger = logging.getLogger()
    fh = logging.FileHandler(WORKER_LOG_FILE)
    root_logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(WORKER_LOG_FORMAT)
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)
    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    return base_logger


class DealifyWorker:

    def __init__(self):
        self.logger = start_logger()
        self.worker_id = WORKER_ID
        if not self.worker_id:
            logging.critical("Can't Initialize Worker - Worker ID is None")
        self.db_creds = DEALIFY_DB_CREDS
        if not self.db_creds['password']:
            logging.critical(
                "Can't Initialize Worker - Database Password is None")
        self.health_check_interval_seconds = 60
        self.task_change_interval_seconds = 20
        self.retry_interval_seconds = 10
        self.max_retries = 10
        self.status = None
        self.started_at = None
        self.allowed_task_types = None
        self.allowed_task_ids = None
        self.current_task = None
        self.loop = asyncio.get_event_loop()
        self.pool = None

    def set_status(self, new_status):
        if not new_status:
            self.logger.critical(
                f"Failed to Set Worker Status - New Status is None")
            return self
        old_status = self.status
        self.status = new_status
        logging.info(
            f"Worker Set Status - Old Status: {old_status} - New Status: {self.status}")
        return self

    def set_current_task(self, new_task):
        if not isinstance(new_task, DealifyTask):
            logging.critical(
                f"Failed to Set Worker Task - Task Must Be Instance of DealifyTask")
            return self
        old_task = self.current_task
        if old_task:
            old_task_id = old_task.task_id
        else:
            old_task_id = None
        self.current_task = new_task
        logging.info(
            f"Worker Set Current Task - Old Task ID: {old_task_id} - New Task ID: {new_task.task_id}")
        return self

    def set_allowed_task_types(self, allowed_task_types):
        if not allowed_task_types:
            logging.critical(
                f"Worker Failed to Set Allowed Task Types - Input is None")
            return self
        old_allowed_task_types = self.allowed_task_types
        self.allowed_task_types = allowed_task_types
        logging.info(
            f"Successfully Set Worker Task Types - Old Task Types: {old_allowed_task_types} - New Task Types: {self.allowed_task_types}")
        return self

    def set_allowed_task_ids(self, task_ids):
        if not task_ids:
            logging.critical(f"Worker Failed to Set Task ID's - Input is None")
            return self
        old_task_ids = self.allowed_task_ids
        self.allowed_task_ids = cycle(task_ids)
        logging.info(
            f"Worker Successfully Set Task ID's - Old Task ID's: {old_task_ids} - New Task ID's: {self.allowed_task_ids}")
        return self

    async def _sync(self):
        worker = await read_model(self.pool, DealifyWorkerModel, read_dealify_worker_by_id_sproc, [self.worker_id])
        if not worker:
            self.logger.critical(
                f"Failed to Update Worker - Worker Not Found for ID"
            )
            return self

        if not worker.worker_status == self.status:
            logging.error(
                f"Worker Status Mismatch, Attempting to Resolve - DB Status: {worker.worker_status} - Real Status: {self.status}")
            self.status = worker.worker_status

        if not worker.task_config.allowed_task_types:
            self.logger.critical(
                f"Failed to Update Task Types - New Task Types is None")
            return self
        if not self.allowed_task_types == worker.task_config.allowed_task_types:
            new_allowed_task_types = worker.task_config.allowed_task_types

            new_allowed_task_ids = []
            for task_type in new_allowed_task_types:
                rows = await run_sproc(self.pool, read_dealify_task_ids_by_type_sproc, [task_type])
                task_ids = list_from_rows(rows)
                if not task_ids:
                    self.logger.error(
                        f"No Task ID's Found for Task Type: {task_type}")
                    continue
                new_allowed_task_ids.extend(task_ids)
            if not new_allowed_task_ids:
                self.logger.critical(
                    f"Failed to Update Task ID's - Found No Task ID's for All Task Types - Task Types: {new_allowed_task_types}")
                return self
            self.set_allowed_task_types(new_allowed_task_types)
            self.set_allowed_task_ids(new_allowed_task_ids)
        else:
            logging.debug(f"Update Self - No Need to Update Tasks")
        logging.info(f"Worker Sync Successful")
        return self

    async def _task(self):
        if not self.pool:
            self.logger.critical("Can't Run - Not Connected to Database")
            return self
        if self.current_task:
            self.logger.debug("Already Have a Task - Exiting")
            return self
        if not self.status == DealifyWorkerStatus.Running.value:
            self.logger.info(
                "Worker Status No Longer Running - Not Retrieving Any More Tasks")
            self.current_task = None
            return self
        next_task_id = next(self.allowed_task_ids)
        new_task = await read_model(self.pool, DealifyTask, read_dealify_task_by_id_sproc, [next_task_id])
        self.set_current_task(new_task)
        logging.debug(f"Worker Task Check Complete")
        return self

    async def _start(self):
        self.started_at = datetime.utcnow()
        if self.pool:
            self.logger.error(
                "Tried to Start while already Connected to Database")
            return self
        self.pool = await start_pool(self.db_creds)
        if not self.pool:
            self.logger.error("Failed to Connect to Database - Exiting")
        else:
            self.logger.info("Successfully Connected to Database")
        await self._sync()
        if not self.status == DealifyWorkerStatus.Started.value:
            self.logger.critical(
                f"Unable to Start Worker - Invalid Status - Required: {DealifyWorkerStatus.Running.value} - Got: {self.status}")
            return self
        await run_sproc(self.pool, update_dealify_worker_status_sproc, [self.worker_id, DealifyWorkerStatus.Running.value])
        await self._sync()
        return self

    async def _shutdown(self):
        if not self.pool:
            self.logger.error(
                f"Tried To Shutdown While Not Connected to Database"
            )
        worker = await read_model(self.pool, DealifyWorkerModel, read_dealify_worker_by_id_sproc, [self.worker_id])
        if not worker:
            self.logger.critical(
                f"Failed to Shutdown Worker - Worker Not Found for ID"
            )
        success = await run_sproc(self.pool, update_dealify_worker_status_sproc, [self.worker_id, DealifyWorkerStatus.Dormont.value])
        if success:
            self.logger.info(
                f"Set Worker Status - Updated Worker from Running to Dormont")
        else:
            self.logger.critical(
                f"Set Worker Status - Failed to Update Worker from Running to Dormont"
            )
        return self

    async def _run(self):
        retries = 0
        while retries < self.max_retries:
            await self._sync()
            await self._task()
            if not self.pool:
                self.logger.critical(
                    f"Can't Run - Not Connected to Database - Attempt {retries} of {self.max_retries}")
                await self._start()
                retries += 1
                continue
            if not self.allowed_task_ids:
                self.logger.critical(
                    f"Can't Run - No Allowed Task ID's - Attempt {retries} of {self.max_retries}")
                retries += 1
                continue
            if not self.current_task:
                self.logger.critical(
                    f"Can't Run - No Tasks - Attempt {retries} of {self.max_retries}")
                retries += 1
                continue
            started_at = perf_counter()
            success = await run_dealify_task(self.current_task, self.pool)
            if success:
                finished_at = perf_counter()
                self.logger.info(
                    f"Sucessfully Executed Task ID: {self.current_task.task_id} - Total Time: {format(finished_at - started_at, '.3f')}s - Sleeping for {self.task_change_interval_seconds}s Before Next Task")
                await asyncio.sleep(self.task_change_interval_seconds)
                self.current_task = None
        await self._shutdown()

    async def work(self):
        await self._start()
        tasks = []
        tasks.append(self._sync())
        tasks.append(self._task())
        tasks.append(self._run())
        await asyncio.gather(*tasks)

    def run(self):
        self.loop.run_until_complete(self.work())


if __name__ == '__main__':
    dw = DealifyWorker()
    dw.run()
