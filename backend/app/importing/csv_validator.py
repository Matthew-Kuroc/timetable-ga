from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, TypeVar

from backend.app.domain.models import (
    AcademicCalendarDate,
    CourseSection,
    Lecturer,
    LecturerTimePreference,
    Room,
    RoomUnavailableSlot,
    TimeSlot,
    TimetableInputData,
)


COURSE_TYPES = {"THEORY", "PRACTICE", "INTEGRATED"}
ROOM_TYPES = {"THEORY_ROOM", "COMPUTER_LAB", "SPECIALIZED_LAB"}
VALID_THEORY_RANGES = {(1, 3), (4, 6), (7, 9), (10, 12), (13, 15)}
VALID_LONG_RANGES = {(1, 5), (1, 6), (2, 6)}
VALID_SHORT_COMPONENT_RANGES = {(1, 2), (2, 3), (4, 5), (5, 6), (7, 8), (8, 9), (10, 11), (11, 12), (13, 14), (14, 15)}


@dataclass(frozen=True)
class CsvValidationError:
    file: str
    row: int | None
    column: str | None
    value: str
    reason: str


@dataclass(frozen=True)
class CsvValidationResult:
    data: TimetableInputData | None
    errors: tuple[CsvValidationError, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors and self.data is not None


def validate_sample_dataset(directory: str | Path) -> CsvValidationResult:
    base_dir = Path(directory)
    errors: list[CsvValidationError] = []

    lecturer_rows = _read_csv(base_dir, "lecturers.csv", _LECTURER_COLUMNS, errors)
    room_rows = _read_csv(base_dir, "rooms.csv", _ROOM_COLUMNS, errors)
    slot_rows = _read_csv(base_dir, "time_slots.csv", _TIME_SLOT_COLUMNS, errors)
    section_rows = _read_csv(base_dir, "course_sections.csv", _COURSE_SECTION_COLUMNS, errors)
    lecturer_preference_rows = _read_csv(
        base_dir,
        "lecturer_time_preferences.csv",
        _LECTURER_TIME_PREFERENCE_COLUMNS,
        errors,
    )
    room_unavailable_rows = _read_csv(
        base_dir,
        "room_unavailable_slots.csv",
        _ROOM_UNAVAILABLE_COLUMNS,
        errors,
    )
    academic_calendar_rows = _read_csv(
        base_dir,
        "academic_calendar.csv",
        _ACADEMIC_CALENDAR_COLUMNS,
        errors,
    )

    lecturers = _build_unique_map(
        "lecturers.csv",
        lecturer_rows,
        "lecturer_code",
        _parse_lecturer,
        errors,
    )
    rooms = _build_unique_map("rooms.csv", room_rows, "room_code", _parse_room, errors)
    time_slots = _build_unique_map(
        "time_slots.csv",
        slot_rows,
        "slot_code",
        _parse_time_slot,
        errors,
    )
    course_sections = _build_unique_map(
        "course_sections.csv",
        section_rows,
        "section_code",
        lambda row, row_number: _parse_course_section(row, row_number, errors),
        errors,
    )
    academic_calendar_dates_by_text = _build_unique_map(
        "academic_calendar.csv",
        academic_calendar_rows,
        "date",
        lambda row, row_number: _parse_academic_calendar_date(row, row_number, errors),
        errors,
    )
    academic_calendar_dates = {
        calendar_date.date: calendar_date
        for calendar_date in academic_calendar_dates_by_text.values()
    }
    _validate_makeup_window_dates(academic_calendar_dates.values(), errors)

    _validate_references(course_sections.values(), lecturers, "course_sections.csv", errors)
    _validate_sections_have_feasible_local_domains(course_sections.values(), rooms, time_slots, errors)

    lecturer_time_preferences = _parse_lecturer_time_preferences(
        lecturer_preference_rows,
        lecturers,
        time_slots,
        errors,
    )
    room_unavailable_slots = _parse_room_unavailable_slots(
        room_unavailable_rows,
        rooms,
        time_slots,
        errors,
    )

    if errors:
        return CsvValidationResult(data=None, errors=tuple(errors))

    return CsvValidationResult(
        data=TimetableInputData(
            lecturers=lecturers,
            rooms=rooms,
            time_slots=time_slots,
            course_sections=course_sections,
            lecturer_time_preferences=tuple(lecturer_time_preferences),
            room_unavailable_slots=tuple(room_unavailable_slots),
            academic_calendar_dates=academic_calendar_dates,
        ),
        errors=(),
    )


_LECTURER_COLUMNS = {
    "lecturer_code",
    "lecturer_name",
    "preferred_days",
    "preferred_slots",
    "undesired_days",
    "undesired_slots",
    "max_days_per_week",
    "max_consecutive_sessions",
}
_ROOM_COLUMNS = {
    "room_code",
    "room_name",
    "capacity",
    "room_type",
    "room_size_category",
    "available",
}
_TIME_SLOT_COLUMNS = {
    "slot_code",
    "day_of_week",
    "start_period",
    "end_period",
    "session_type",
    "supports_course_types",
    "active",
}
_COURSE_SECTION_COLUMNS = {
    "course_code",
    "course_name",
    "section_code",
    "lecturer_code",
    "course_type",
    "required_room_type",
    "required_sessions",
    "weekly_sessions",
    "second_session_periods",
    "periods_per_session",
    "expected_students",
    "initial_registration_limit",
    "approved_max_students",
    "scheduling_student_count",
    "start_date",
    "end_date",
}
_LECTURER_TIME_PREFERENCE_COLUMNS = {"lecturer_code", "slot_code", "mandatory", "reason"}
_ROOM_UNAVAILABLE_COLUMNS = {"room_code", "slot_code", "reason"}
_ACADEMIC_CALENDAR_COLUMNS = {
    "date",
    "academic_week",
    "day_of_week",
    "is_teaching_day",
    "is_holiday",
    "holiday_name",
    "note",
}


def _read_csv(
    base_dir: Path,
    file_name: str,
    required_columns: set[str],
    errors: list[CsvValidationError],
) -> list[tuple[int, dict[str, str]]]:
    path = base_dir / file_name
    if not path.exists():
        errors.append(_error(file_name, None, None, "", "Không tìm thấy file CSV bắt buộc"))
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            fieldnames = set(reader.fieldnames or [])
            missing = sorted(required_columns - fieldnames)
            if missing:
                errors.append(
                    _error(file_name, 1, None, ",".join(missing), "Thiếu cột bắt buộc")
                )
                return []
            return [
                (row_number, {key: (value or "").strip() for key, value in row.items()})
                for row_number, row in enumerate(reader, start=2)
            ]
    except UnicodeDecodeError:
        errors.append(_error(file_name, None, None, "", "File phải dùng mã hóa UTF-8"))
    except csv.Error as exc:
        errors.append(_error(file_name, None, None, "", f"File CSV không hợp lệ: {exc}"))
    return []


T = TypeVar("T")


def _build_unique_map(
    file_name: str,
    rows: Iterable[tuple[int, dict[str, str]]],
    key_column: str,
    parser: Callable[[dict[str, str], int], T | None],
    errors: list[CsvValidationError],
) -> dict[str, T]:
    values: dict[str, T] = {}
    seen_rows: dict[str, int] = {}
    for row_number, row in rows:
        key = row.get(key_column, "").strip()
        if not key:
            errors.append(_error(file_name, row_number, key_column, key, "Giá trị bắt buộc bị trống"))
            continue
        if key in values:
            first_row = seen_rows[key]
            errors.append(
                _error(
                    file_name,
                    row_number,
                    key_column,
                    key,
                    f"Mã bị trùng với dòng {first_row}",
                )
            )
            continue
        parsed = parser(row, row_number)
        if parsed is not None:
            values[key] = parsed
            seen_rows[key] = row_number
    return values


def _parse_lecturer(row: dict[str, str], row_number: int) -> Lecturer | None:
    return Lecturer(
        lecturer_code=row["lecturer_code"],
        lecturer_name=row["lecturer_name"],
        preferred_days=_parse_int_list(row.get("preferred_days", "")),
        preferred_slots=_parse_string_list(row.get("preferred_slots", "")),
        undesired_days=_parse_int_list(row.get("undesired_days", "")),
        undesired_slots=_parse_string_list(row.get("undesired_slots", "")),
        max_days_per_week=_optional_int(row.get("max_days_per_week", "")),
        max_consecutive_sessions=_optional_int(row.get("max_consecutive_sessions", "")),
    )


def _parse_room(row: dict[str, str], row_number: int) -> Room | None:
    capacity = _required_positive_int("rooms.csv", row_number, "capacity", row["capacity"])
    if capacity is None:
        return None
    room_type = row["room_type"]
    if room_type not in ROOM_TYPES:
        # The caller keeps parsing other rows so one bad dictionary value does not hide later errors.
        return None
    return Room(
        room_code=row["room_code"],
        room_name=row["room_name"],
        capacity=capacity,
        room_type=room_type,
        room_size_category=row["room_size_category"],
        available=_parse_bool(row["available"]),
    )


def _parse_time_slot(row: dict[str, str], row_number: int) -> TimeSlot | None:
    day = _required_int("time_slots.csv", row_number, "day_of_week", row["day_of_week"])
    start = _required_positive_int("time_slots.csv", row_number, "start_period", row["start_period"])
    end = _required_positive_int("time_slots.csv", row_number, "end_period", row["end_period"])
    if day is None or start is None or end is None:
        return None
    if day < 2 or day > 8 or end < start:
        return None
    if (start, end) not in VALID_THEORY_RANGES | VALID_LONG_RANGES | VALID_SHORT_COMPONENT_RANGES:
        return None
    return TimeSlot(
        slot_code=row["slot_code"],
        day_of_week=day,
        start_period=start,
        end_period=end,
        supports_course_types=_parse_string_list(row["supports_course_types"]),
        active=_parse_bool(row["active"]),
    )


def _parse_course_section(
    row: dict[str, str],
    row_number: int,
    errors: list[CsvValidationError],
) -> CourseSection | None:
    course_type = row["course_type"]
    required_room_type = row["required_room_type"]
    if course_type not in COURSE_TYPES:
        errors.append(_error("course_sections.csv", row_number, "course_type", course_type, "Loại học phần không hợp lệ"))
        return None
    if required_room_type not in ROOM_TYPES:
        errors.append(_error("course_sections.csv", row_number, "required_room_type", required_room_type, "Loại phòng yêu cầu không hợp lệ"))
        return None

    periods = _required_positive_int("course_sections.csv", row_number, "periods_per_session", row["periods_per_session"])
    required_sessions = _required_positive_int("course_sections.csv", row_number, "required_sessions", row["required_sessions"])
    weekly_sessions = _required_positive_int("course_sections.csv", row_number, "weekly_sessions", row["weekly_sessions"])
    second_session_periods = _optional_int(row.get("second_session_periods", ""))
    expected_students = _required_positive_int("course_sections.csv", row_number, "expected_students", row["expected_students"])
    initial_limit = _optional_int(row["initial_registration_limit"])
    approved_max = _optional_int(row["approved_max_students"])
    imported_scheduling_count = _optional_int(row["scheduling_student_count"])
    start_date = _parse_date(row["start_date"])
    end_date = _parse_date(row["end_date"])
    if periods is None or required_sessions is None or weekly_sessions is None or expected_students is None:
        return None
    if weekly_sessions not in {1, 2}:
        errors.append(_error("course_sections.csv", row_number, "weekly_sessions", str(weekly_sessions), "Số buổi trong tuần chỉ được là 1 hoặc 2"))
        return None
    if weekly_sessions == 1 and second_session_periods is not None:
        errors.append(_error("course_sections.csv", row_number, "second_session_periods", str(second_session_periods), "Không được khai báo buổi thứ hai khi weekly_sessions=1"))
        return None
    if weekly_sessions == 2 and course_type == "THEORY":
        errors.append(_error("course_sections.csv", row_number, "weekly_sessions", str(weekly_sessions), "THEORY chỉ được khai báo một buổi mỗi tuần"))
        return None
    if weekly_sessions == 2 and (periods != 3 or second_session_periods not in {2, 3}):
        errors.append(_error("course_sections.csv", row_number, "periods_per_session/second_session_periods", f"{periods}+{second_session_periods or ''}", "Mẫu nhiều buổi hiện chỉ hỗ trợ 3+2 hoặc 3+3"))
        return None
    if start_date is None or end_date is None or end_date < start_date:
        errors.append(_error("course_sections.csv", row_number, "start_date/end_date", f"{row['start_date']}..{row['end_date']}", "Khoảng ngày của lớp học phần không hợp lệ"))
        return None

    computed_scheduling_count = approved_max or initial_limit or expected_students
    scheduling_count = imported_scheduling_count or computed_scheduling_count
    if scheduling_count != computed_scheduling_count:
        errors.append(
            _error(
                "course_sections.csv",
                row_number,
                "scheduling_student_count",
                str(scheduling_count),
                "Số lượng sinh viên xếp lịch không khớp quy tắc ưu tiên",
            )
        )
        return None

    return CourseSection(
        section_code=row["section_code"],
        course_code=row["course_code"],
        course_name=row["course_name"],
        lecturer_code=row["lecturer_code"],
        course_type=course_type,
        required_room_type=required_room_type,
        periods_per_session=periods,
        required_sessions=required_sessions,
        weekly_sessions=weekly_sessions,
        second_session_periods=second_session_periods,
        expected_students=expected_students,
        initial_registration_limit=initial_limit,
        approved_max_students=approved_max,
        scheduling_student_count=scheduling_count,
        start_date=start_date,
        end_date=end_date,
    )


def _parse_academic_calendar_date(
    row: dict[str, str],
    row_number: int,
    errors: list[CsvValidationError],
) -> AcademicCalendarDate | None:
    parsed_date = _parse_date(row["date"])
    academic_week = _required_positive_int("academic_calendar.csv", row_number, "academic_week", row["academic_week"])
    day_of_week = _required_int("academic_calendar.csv", row_number, "day_of_week", row["day_of_week"])
    if parsed_date is None or academic_week is None or day_of_week is None:
        errors.append(_error("academic_calendar.csv", row_number, None, row["date"], "Ngày học kỳ không hợp lệ"))
        return None
    if day_of_week < 2 or day_of_week > 8:
        errors.append(_error("academic_calendar.csv", row_number, "day_of_week", str(day_of_week), "Thứ phải nằm trong khoảng 2 đến 8"))
        return None
    return AcademicCalendarDate(
        date=parsed_date,
        academic_week=academic_week,
        day_of_week=day_of_week,
        is_teaching_day=_parse_bool(row["is_teaching_day"]),
        is_holiday=_parse_bool(row["is_holiday"]),
        holiday_name=row["holiday_name"],
        note=row["note"],
    )


def _validate_makeup_window_dates(
    calendar_dates: Iterable[AcademicCalendarDate],
    errors: list[CsvValidationError],
) -> None:
    available_weeks = {
        calendar_date.academic_week
        for calendar_date in calendar_dates
        if calendar_date.is_teaching_day and not calendar_date.is_holiday
    }
    for academic_week in (16, 17, 18):
        if academic_week not in available_weeks:
            errors.append(
                _error(
                    "academic_calendar.csv",
                    None,
                    "academic_week",
                    str(academic_week),
                    "Thiếu ngày giảng dạy hợp lệ cho cửa sổ học bù tuần 16-18",
                )
            )


def _validate_references(
    sections: Iterable[CourseSection],
    lecturers: dict[str, Lecturer],
    file_name: str,
    errors: list[CsvValidationError],
) -> None:
    for section in sections:
        if section.lecturer_code not in lecturers:
            errors.append(
                _error(
                    file_name,
                    None,
                    "lecturer_code",
                    section.lecturer_code,
                    f"Mã giảng viên của lớp {section.section_code} không tồn tại",
                )
            )


def _validate_sections_have_feasible_local_domains(
    sections: Iterable[CourseSection],
    rooms: dict[str, Room],
    time_slots: dict[str, TimeSlot],
    errors: list[CsvValidationError],
) -> None:
    active_slots = [slot for slot in time_slots.values() if slot.active]
    available_rooms = [room for room in rooms.values() if room.available]

    for section in sections:
        compatible_slot_exists = any(_slot_supports_section(slot, section, 1) for slot in active_slots)
        if section.weekly_sessions == 2:
            compatible_slot_exists = compatible_slot_exists and any(_slot_supports_section(slot, section, 2) for slot in active_slots)
        if not compatible_slot_exists:
            errors.append(
                _error(
                    "course_sections.csv",
                    None,
                    "periods_per_session",
                    str(section.periods_per_session),
                    f"Lớp {section.section_code} không có khung giờ phù hợp",
                )
            )

        compatible_room_exists = any(
            room.room_type == section.required_room_type
            and room.capacity >= section.scheduling_student_count
            for room in available_rooms
        )
        if not compatible_room_exists:
            errors.append(
                _error(
                    "course_sections.csv",
                    None,
                    "required_room_type",
                    section.required_room_type,
                    f"Lớp {section.section_code} không có phòng phù hợp về loại phòng và sức chứa",
                )
            )


def _slot_supports_section(slot: TimeSlot, section: CourseSection, meeting_number: int = 1) -> bool:
    if section.course_type not in slot.supports_course_types:
        return False
    periods = section.second_session_periods if meeting_number == 2 else section.periods_per_session
    valid_ranges = VALID_THEORY_RANGES if section.course_type == "THEORY" else VALID_THEORY_RANGES | VALID_LONG_RANGES | VALID_SHORT_COMPONENT_RANGES
    return (slot.start_period, slot.end_period) in valid_ranges and slot.duration == periods


def _parse_lecturer_time_preferences(
    rows: list[tuple[int, dict[str, str]]],
    lecturers: dict[str, Lecturer],
    time_slots: dict[str, TimeSlot],
    errors: list[CsvValidationError],
) -> list[LecturerTimePreference]:
    values: list[LecturerTimePreference] = []
    for row_number, row in rows:
        lecturer_code = row["lecturer_code"]
        slot_code = row["slot_code"]
        if lecturer_code not in lecturers:
            errors.append(_error("lecturer_time_preferences.csv", row_number, "lecturer_code", lecturer_code, "Mã giảng viên không tồn tại"))
            continue
        if slot_code not in time_slots:
            errors.append(_error("lecturer_time_preferences.csv", row_number, "slot_code", slot_code, "Mã khung giờ không tồn tại"))
            continue
        values.append(
            LecturerTimePreference(
                lecturer_code=lecturer_code,
                slot_code=slot_code,
                mandatory=_parse_bool(row["mandatory"]),
                reason=row["reason"],
            )
        )
    return values


def _parse_room_unavailable_slots(
    rows: list[tuple[int, dict[str, str]]],
    rooms: dict[str, Room],
    time_slots: dict[str, TimeSlot],
    errors: list[CsvValidationError],
) -> list[RoomUnavailableSlot]:
    values: list[RoomUnavailableSlot] = []
    for row_number, row in rows:
        room_code = row["room_code"]
        slot_code = row["slot_code"]
        if room_code not in rooms:
            errors.append(_error("room_unavailable_slots.csv", row_number, "room_code", room_code, "Mã phòng không tồn tại"))
            continue
        if slot_code not in time_slots:
            errors.append(_error("room_unavailable_slots.csv", row_number, "slot_code", slot_code, "Mã khung giờ không tồn tại"))
            continue
        values.append(RoomUnavailableSlot(room_code=room_code, slot_code=slot_code, reason=row["reason"]))
    return values


def _parse_string_list(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


def _parse_int_list(value: str) -> tuple[int, ...]:
    parsed: list[int] = []
    for item in value.split("|"):
        item = item.strip()
        if item:
            parsed.append(int(item))
    return tuple(parsed)


def _optional_int(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    return int(value)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _required_int(file_name: str, row: int, column: str, value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _required_positive_int(file_name: str, row: int, column: str, value: str) -> int | None:
    parsed = _required_int(file_name, row, column, value)
    if parsed is None or parsed <= 0:
        return None
    return parsed


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def _error(
    file_name: str,
    row: int | None,
    column: str | None,
    value: str,
    reason: str,
) -> CsvValidationError:
    return CsvValidationError(file=file_name, row=row, column=column, value=value, reason=reason)
