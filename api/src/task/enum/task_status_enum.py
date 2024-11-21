from enum import Enum


class TaskStatusEnum(str, Enum):
    INIT = "init"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
