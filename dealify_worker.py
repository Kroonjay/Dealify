import asyncio
import logging
from config import DEALIFY_DB_CREDS, WORKER_LOG_FILE
from database_helpers import connect_dealify_db, start_next_dealify_search_task
from models import DealifySearchTask
from dealify_helpers import execute_dealify_search_task, start_logger
from datetime import datetime


class DealifyWorker:

    def __init__(self):
        self.logger = start_logger()
        self.db_creds = DEALIFY_DB_CREDS
        if not self.db_creds['password']:
            logging.critical("Can't Connect to Database - Password Missing")
        self.health_check_interval_seconds = 60
        self.task_change_interval_seconds = 60
        self.started_at = None
        self.task_id = 0
        self.current_task = None
        self.loop = asyncio.get_event_loop()
        self.conn = None

    async def _task(self):
        if not self.conn:
            self.logger.critical("Can't Run - Not Connected to Database")
            return self
        if self.current_task:
            self.logger.info("Already Have a Task - Exiting")
            return self
        self.current_task = await start_next_dealify_search_task(self.conn)
        if self.current_task:
            self.task_id = self.current_task.task_id
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
        return self

    async def _run(self):

        while True:
            if not self.conn:
                self.logger.critical("Can't Run - Not Connected to Database")
                await self._start()
                continue
            await self._task()
            if not self.current_task:
                self.logger.critical("Couldn't Get a Task - Exiting")
                return None
            success = await execute_dealify_search_task(self.current_task, self.conn)
            if success:
                self.logger.info(
                    "sucessfully executed task - Sleeping for 60s")
                await asyncio.sleep(60)

    def work(self):
        self.loop.run_until_complete(self._run())


if __name__ == '__main__':
    dw = DealifyWorker()
    dw.work()
