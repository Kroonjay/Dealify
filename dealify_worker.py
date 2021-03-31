import asyncio
import logging
from config import DEALIFY_DB_CREDS, WORKER_LOG_FILE, WORKER_ID
from database_helpers import connect_dealify_db, disconnect_dealify_db, start_next_dealify_search_task, read_dealify_worker_by_id, read_dealify_task_ids_by_type, read_dealify_search_task_by_id, update_dealify_worker_status
from models import DealifySearchTask, DealifyWorkerStatus
from dealify_helpers import execute_dealify_search_task, start_logger, set_worker_status
from datetime import datetime
from itertools import cycle


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
        self.conn = None

    async def _set_status(self, worker):
        worker_status = worker.worker_status
        if worker_status is None:
            self.logger.critical(
                f"Failed to Set Worker Status - New Status is None")
            return self
        if not self.status:
            if not worker_status == DealifyWorkerStatus.Started.value:
                self.logger.critical(
                    f"Set Worker Status - Failed to Initialize Worker - Worker Status Must Be {DealifyWorkerStatus.Started.value}, Got {worker_status}"
                )
                return self
            success = await set_worker_status(worker, DealifyWorkerStatus.Running.value, self.conn)
            if success:
                self.logger.info(
                    f"Set Worker Status - Updated Worker from Started to Running")
            else:
                self.logger.critical(
                    f"Set Worker Status - Failed to Update Worker from Started to Running"
                )
            self.logger.info(
                f"Set Worker Status - Successfully Initialized Worker Status - Status: {self.status}")
        elif self.status == worker_status:
            self.logger.debug(
                f"Set Worker Status - No Change - Status: {self.status}")
            return self

        elif self.status == DealifyWorkerStatus.Killed.value:
            self.logger.critical(
                f"Set Worker Status - Kill Requested, Worker Will Quit After Current Task")
        elif self.status == DealifyWorkerStatus.Dormont.value:
            self.logger.critical(
                f"Set Worker Status - Dormont Status Discovered, Shouldn't Be Possible")
        else:
            self.logger.critical(
                f"Set Worker Status - Worker Has Unsupported Status - Status: {self.status}"
            )
        updated_worker = await read_dealify_worker_by_id(self.worker_id, self.conn)
        self.status = updated_worker.worker_status
        return self

    async def _update_self(self):
        worker = await read_dealify_worker_by_id(self.worker_id, self.conn)
        if not worker:
            self.logger.critical(
                f"Failed to Update Worker - Worker Not Found for ID"
            )
        await self._set_status(worker)
        if not worker.task_config.allowed_task_types:
            self.logger.critical(
                f"Failed to Update Task Types - New Task Types is None")
            return self
        if not self.allowed_task_types == worker.task_config.allowed_task_types:
            new_allowed_task_types = worker.task_config.allowed_task_types

            new_allowed_task_ids = []
            for task_type in new_allowed_task_types:
                task_ids = await read_dealify_task_ids_by_type(task_type, self.conn)
                new_allowed_task_ids.extend(task_ids)
            if not new_allowed_task_ids:
                self.logger.critical(
                    f"Failed to Update Task ID's - Found No Task ID's for All Task Types - Task Types: {new_allowed_task_types}")
                return self
            self.allowed_task_types = new_allowed_task_types
            self.allowed_task_ids = cycle(new_allowed_task_ids)
            self.logger.info(
                f"Allowed Task Types Updated - Old Values: {self.allowed_task_types} - New Values: {new_allowed_task_types}")
        else:
            logging.debug(f"Update Self - No Need to Update Tasks")
        return self

    async def _task(self):
        if not self.conn:
            self.logger.critical("Can't Run - Not Connected to Database")
            return self
        if self.current_task:
            self.logger.info("Already Have a Task - Exiting")
            return self
        if not self.status == DealifyWorkerStatus.Running.value:
            self.logger.info(
                "Worker Status No Longer Running - Not Retrieving Any More Tasks")
            self.current_task = None
            return self
        next_task_id = next(self.allowed_task_ids)
        self.current_task = await read_dealify_search_task_by_id(next_task_id, self.conn)
        return self

    async def _start(self):
        self.started_at = datetime.utcnow()
        if self.conn:
            self.logger.error(
                "Tried to Start while already Connected to Database")
            return self
        self.conn = await connect_dealify_db(self.db_creds)
        if not self.conn:
            self.logger.error("Failed to Connect to Database - Exiting")
        else:
            self.logger.info("Successfully Connected to Database")
        await self._update_self()
        return self

    async def _shutdown(self):
        if not self.conn:
            self.logger.error(
                f"Tried To Shutdown While Not Connected to Database"
            )
        worker = await read_dealify_worker_by_id(self.worker_id, self.conn)
        if not worker:
            self.logger.critical(
                f"Failed to Shutdown Worker - Worker Not Found for ID"
            )
        success = await set_worker_status(worker, DealifyWorkerStatus.Dormont.value, self.conn)
        if success:
            self.logger.info(
                f"Set Worker Status - Updated Worker from Running to Dormont")
        else:
            self.logger.critical(
                f"Set Worker Status - Failed to Update Worker from Running to Dormont"
            )
        disconnect_dealify_db(self.conn)
        return self

    async def _run(self):
        retries = 0
        while retries < self.max_retries:
            if not self.conn:
                self.logger.critical(
                    f"Can't Run - Not Connected to Database - Attempt {retries} of {self.max_retries}")
                await self._start()
                retries += 1
                continue
            await self._update_self()
            if not self.allowed_task_ids:
                self.logger.critical(
                    f"Can't Run - No Allowed Task ID's - Attempt {retries} of {self.max_retries}")
                retries += 1
                continue
            await self._task()
            if not self.current_task:
                self.logger.critical(
                    f"Can't Run - No Tasks - Attempt {retries} of {self.max_retries}")
                retries += 1
                continue
            success = await execute_dealify_search_task(self.current_task, self.conn)
            if success:
                self.logger.info(
                    f"sucessfully executed Task ID: {self.current_task.task_id} - Sleeping for {self.task_change_interval_seconds}s Before Next Task")
                await asyncio.sleep(self.task_change_interval_seconds)
                self.current_task = None
        await self._shutdown()

    def work(self):
        self.loop.run_until_complete(self._run())


if __name__ == '__main__':
    dw = DealifyWorker()
    dw.work()
