from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Lecturer:
    lecturer_code: str
    lecturer_name: str
    preferred_days: tuple[int, ...] = ()
    preferred_slots: tuple[str, ...] = ()
    undesired_days: tuple[int, ...] = ()
    undesired_slots: tuple[str, ...] = ()
    max_days_per_week: int | None = None
    max_consecutive_sessions: int | None = None


@dataclass(frozen=True)
class Room:
    room_code: str
    room_name: str
    capacity: int
    room_type: str
    room_size_category: str
    available: bool


@dataclass(frozen=True)
class TimeSlot:
    slot_code: str
    day_of_week: int
    start_period: int
    end_period: int
    supports_course_types: tuple[str, ...]
    active: bool

    @property
    def duration(self) -> int:
        return self.end_period - self.start_period + 1


@dataclass(frozen=True)
class CourseSection:
    section_code: str
    course_code: str
    course_name: str
    lecturer_code: str
    course_type: str
    required_room_type: str
    periods_per_session: int
    required_sessions: int
    weekly_sessions: int
    second_session_periods: int | None
    expected_students: int
    initial_registration_limit: int | None
    approved_max_students: int | None
    scheduling_student_count: int
    start_date: date
    end_date: date


@dataclass(frozen=True)
class LecturerTimePreference:
    lecturer_code: str
    slot_code: str
    mandatory: bool
    reason: str = ""


@dataclass(frozen=True)
class RoomUnavailableSlot:
    room_code: str
    slot_code: str
    reason: str = ""


@dataclass(frozen=True)
class AcademicCalendarDate:
    date: date
    academic_week: int
    day_of_week: int
    is_teaching_day: bool
    is_holiday: bool
    holiday_name: str = ""
    note: str = ""


@dataclass(frozen=True)
class ScheduleAssignment:
    section_code: str
    room_code: str
    slot_code: str
    meeting_number: int = 1


@dataclass(frozen=True)
class FeasibleAssignmentDomain:
    section_code: str
    meeting_number: int
    assignments: tuple[ScheduleAssignment, ...]


@dataclass(frozen=True)
class HardConstraintViolation:
    code: str
    message: str
    section_code: str | None = None
    other_section_code: str | None = None
    lecturer_code: str | None = None
    room_code: str | None = None
    slot_code: str | None = None


@dataclass(frozen=True)
class ScheduleOccurrence:
    section_code: str
    room_code: str
    slot_code: str
    date: date
    academic_week: int
    status: str = "SCHEDULED"
    meeting_number: int = 1


@dataclass(frozen=True)
class SkippedHolidaySession:
    section_code: str
    room_code: str
    slot_code: str
    date: date
    academic_week: int
    holiday_name: str
    meeting_number: int = 1


@dataclass(frozen=True)
class TimetableInputData:
    lecturers: dict[str, Lecturer]
    rooms: dict[str, Room]
    time_slots: dict[str, TimeSlot]
    course_sections: dict[str, CourseSection]
    lecturer_time_preferences: tuple[LecturerTimePreference, ...]
    room_unavailable_slots: tuple[RoomUnavailableSlot, ...]
    academic_calendar_dates: dict[date, AcademicCalendarDate]
