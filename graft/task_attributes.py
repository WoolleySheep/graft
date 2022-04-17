import dataclasses
import datetime
from typing import Optional

from graft.duration import Duration
from graft.priority import Priority
from graft.progress import Progress


class TaskCompletedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Task is already completed", *args, **kwargs)


class TaskBlockedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Task is blocked", *args, **kwargs)


class TaskNotBlockedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Task is not blocked", *args, **kwargs)


class AfterDueDatetimeError(Exception):
    def __init__(self, start_datetime, due_datetime, *args, **kwargs):
        self.start_datetime = start_datetime
        self.due_datetime = due_datetime

        formatted_start = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_due = due_datetime.strftime("%Y-%m-%d %H:%M:%S")

        super().__init__(
            f"Start datetime [{formatted_start}] is after due datetime [{formatted_due}]",
            *args,
            **kwargs,
        )


class BeforeStartDatetimeError(Exception):
    def __init__(self, start_datetime, due_datetime, *args, **kwargs):
        self.start_datetime = start_datetime
        self.due_datetime = due_datetime

        formatted_start = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_due = due_datetime.strftime("%Y-%m-%d %H:%M:%S")

        super().__init__(
            f"Due datetime [{formatted_due}] is before start datetime [{formatted_start}]",
            *args,
            **kwargs,
        )


class NotStartedToCompletedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "Cannot progress from 'not started' to 'completed'", *args, **kwargs
        )


class TaskStartedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Task is already started", *args, **kwargs)


@dataclasses.dataclass
class TaskAttributes:
    name: str = ""
    description: str = ""
    priority: Optional[Priority] = None
    progress: Optional[Progress] = Progress.NOT_STARTED
    duration: Optional[Duration] = None
    blocked: bool = False
    due_datetime: Optional[datetime.datetime] = None
    start_datetime: Optional[datetime.datetime] = None

    @classmethod
    def from_json_serializable_dict(cls, data: dict):
        return cls(
            name=data["name"],
            description=data["description"],
            priority=Priority(data["priority"]) if data["priority"] else None,
            progress=Progress(data["progress"]) if data["progress"] else None,
            duration=Duration(data["duration"]) if data["duration"] else None,
            blocked=data["blocked"],
            due_datetime=datetime.datetime.strptime(
                data["due_datetime"], "%Y-%m-%d %H:%M:%S"
            )
            if data["due_datetime"]
            else None,
            start_datetime=datetime.datetime.strptime(
                data["start_datetime"], "%Y-%m-%d %H:%M:%S"
            )
            if data["start_datetime"]
            else None,
        )

    def to_json_serializable_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value if self.priority else None,
            "progress": self.progress.value if self.progress else None,
            "duration": self.duration.value if self.duration else None,
            "blocked": self.blocked,
            "due_datetime": self.due_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if self.due_datetime
            else None,
            "start_datetime": self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
            if self.start_datetime
            else None,
        }

    @property
    def started(self) -> bool:
        return self.progress in (Progress.IN_PROGRESS, Progress.COMPLETED)

    def set_progress(self, progress: Progress) -> None:

        # TODO: Decide whether to reject no-op input (eg: in progress -> in progress)

        if self.blocked:
            raise TaskBlockedError

        if self.progress is Progress.NOT_STARTED and progress is Progress.COMPLETED:
            raise NotStartedToCompletedError

        self.progress = progress

    def clear_progress(self) -> None:
        """Use when changing task into a non-concrete task"""
        if self.progress is not Progress.NOT_STARTED:
            raise TaskStartedError

        self.progress = None

    def block(self) -> None:
        if self.blocked:
            raise TaskBlockedError

        if self.progress is Progress.COMPLETED:
            raise TaskCompletedError

        self.blocked = True

    def unblock(self) -> None:
        if not self.blocked:
            raise TaskNotBlockedError

        self.blocked = False

    def set_start_datetime(self, start_datetime: datetime.datetime) -> None:
        if self.due_datetime and start_datetime >= self.due_datetime:
            raise AfterDueDatetimeError(
                start_datetime=start_datetime, due_datetime=self.due_datetime
            )

        self.start_datetime = start_datetime

    def set_due_datetime(self, due_datetime: datetime.datetime) -> None:
        if self.start_datetime and due_datetime <= self.start_datetime:
            raise BeforeStartDatetimeError(
                start_datetime=self.start_datetime, due_datetime=due_datetime
            )

        self.due_datetime = due_datetime
