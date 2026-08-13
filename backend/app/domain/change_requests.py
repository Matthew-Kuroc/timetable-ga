from __future__ import annotations

from enum import StrEnum


class ScheduleChangeRequestType(StrEnum):
    SUSPEND_ONE_OCCURRENCE = "SUSPEND_ONE_OCCURRENCE"
    MOVE_ONE_OCCURRENCE = "MOVE_ONE_OCCURRENCE"
    MOVE_RECURRING_SCHEDULE = "MOVE_RECURRING_SCHEDULE"


class ScheduleChangeRequestStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    APPLIED = "APPLIED"

