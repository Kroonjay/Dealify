from enum import IntEnum


class DealifyWorkerStatus(IntEnum):
    Dormont = 0
    Running = 1
    Started = 5
    Killed = 6  # Admin Kill Requested, Will Finish Current Task but won't start new One
    Error = 7


class DealifySearchStatus(IntEnum):
    Dormant = 0  # Enabled, but not running and not yet due
    Running = 1  # Worker is actively running Search
    Overdue = 2  # Enabled, but not running and past due
    Disabled = 3  # User Disabled
    New = 4  # Newly Created Search, set for all new searches until queries are built
    Killed = 6  # Admin Disabled
    Error = 7  # App reported Error
