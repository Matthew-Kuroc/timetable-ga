"""Generate a reproducible, anonymous university-scale seven-file CSV batch."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


def generate(output: Path, *, seed: int = 42, lecturers: int = 600, sections: int = 3000, rooms: int = 150) -> dict[str, int | str]:
    if lecturers < 1 or sections < 1 or rooms < 1:
        raise ValueError("Các quy mô phải lớn hơn 0.")
    rng = random.Random(seed)
    output.mkdir(parents=True, exist_ok=True)
    lecturer_rows = _lecturers(lecturers)
    room_rows = _rooms(rooms)
    slot_rows = _slots()
    section_rows = _sections(rng, lecturers, sections, room_rows)
    _write(output / "lecturers.csv", lecturer_rows, ["lecturer_code", "lecturer_name", "preferred_days", "preferred_slots", "undesired_days", "undesired_slots", "max_days_per_week", "max_consecutive_sessions"])
    _write(output / "rooms.csv", room_rows, ["room_code", "room_name", "capacity", "room_type", "room_size_category", "available"])
    _write(output / "time_slots.csv", slot_rows, ["slot_code", "day_of_week", "start_period", "end_period", "session_type", "supports_course_types", "active"])
    _write(output / "course_sections.csv", section_rows, ["course_code", "course_name", "section_code", "lecturer_code", "required_sessions", "weekly_sessions", "periods_per_session", "second_session_periods", "expected_students", "initial_registration_limit", "approved_max_students", "scheduling_student_count", "course_type", "required_room_type", "start_date", "end_date", "campus_code", "notes"])
    preference_rows = _preferences(lecturer_rows, slot_rows)
    _write(output / "lecturer_time_preferences.csv", preference_rows, ["lecturer_code", "slot_code", "mandatory", "reason"])
    unavailable_rows = _room_unavailability(room_rows, slot_rows, rng)
    _write(output / "room_unavailable_slots.csv", unavailable_rows, ["room_code", "slot_code", "reason"])
    calendar_rows = _calendar()
    _write(output / "academic_calendar.csv", calendar_rows, ["date", "academic_week", "day_of_week", "is_teaching_day", "is_holiday", "holiday_name", "note"])
    return {"seed": seed, "lecturers": lecturers, "sections": sections, "rooms": rooms, "time_slots": len(slot_rows), "calendar_dates": len(calendar_rows), "two_meeting_sections": sum(row["weekly_sessions"] == "2" for row in section_rows)}


def _lecturers(count: int) -> list[dict[str, str]]:
    rows = []
    for index in range(1, count + 1):
        code = f"GV{index:04d}"
        preferred_day = 2 + (index % 7)
        rows.append({"lecturer_code": code, "lecturer_name": f"Giảng viên tổng hợp {index:04d}", "preferred_days": str(preferred_day), "preferred_slots": f"D{preferred_day}_1_3", "undesired_days": str(2 + ((index + 3) % 7)), "undesired_slots": f"D{2 + ((index + 3) % 7)}_13_15", "max_days_per_week": "5", "max_consecutive_sessions": "4"})
    return rows


def _rooms(count: int) -> list[dict[str, str]]:
    rows = []
    types = [("THEORY_ROOM", 130, "STANDARD"), ("COMPUTER_LAB", 130, "STANDARD"), ("SPECIALIZED_LAB", 130, "STANDARD"), ("THEORY_ROOM", 130, "LARGE")]
    for index in range(1, count + 1):
        room_type, capacity, category = types[(index - 1) % len(types)]
        rows.append({"room_code": f"R{index:03d}", "room_name": f"Phòng tổng hợp {index:03d}", "capacity": str(capacity), "room_type": room_type, "room_size_category": category, "available": "true"})
    return rows


def _slots() -> list[dict[str, str]]:
    ranges = [((1, 3), "SANG", "THEORY|PRACTICE|INTEGRATED"), ((4, 6), "SANG", "THEORY|PRACTICE|INTEGRATED"), ((7, 9), "CHIEU", "THEORY|PRACTICE|INTEGRATED"), ((10, 12), "CHIEU", "THEORY|PRACTICE|INTEGRATED"), ((13, 15), "TOI", "THEORY|PRACTICE|INTEGRATED"), ((1, 5), "SANG", "PRACTICE|INTEGRATED"), ((1, 6), "SANG", "PRACTICE|INTEGRATED"), ((2, 6), "SANG", "PRACTICE|INTEGRATED")]
    rows = []
    for day in range(2, 9):
        for (start, end), session_type, supported in ranges:
            rows.append({"slot_code": f"D{day}_{start}_{end}", "day_of_week": str(day), "start_period": str(start), "end_period": str(end), "session_type": session_type, "supports_course_types": supported, "active": "true"})
        for start, end in ((1, 2), (2, 3), (4, 5), (5, 6), (7, 8), (8, 9), (10, 11), (11, 12), (13, 14), (14, 15)):
            rows.append({"slot_code": f"D{day}_{start}_{end}", "day_of_week": str(day), "start_period": str(start), "end_period": str(end), "session_type": "COMPONENT", "supports_course_types": "PRACTICE|INTEGRATED", "active": "true"})
    return rows


def _sections(rng: random.Random, lecturer_count: int, count: int, rooms: list[dict[str, str]]) -> list[dict[str, str]]:
    room_types = ["THEORY_ROOM", "COMPUTER_LAB", "SPECIALIZED_LAB"]
    rows = []
    for index in range(1, count + 1):
        course_type = ("THEORY", "PRACTICE", "INTEGRATED")[(index - 1) % 3]
        two_meetings = course_type != "THEORY" and index % 10 in {0, 1, 2}
        periods = 3 if course_type == "THEORY" or two_meetings else (5 if index % 2 else 6)
        second = 2 if two_meetings and index % 2 == 0 else (3 if two_meetings else "")
        required_room = "THEORY_ROOM" if course_type == "THEORY" else ("COMPUTER_LAB" if course_type == "PRACTICE" else room_types[index % len(room_types)])
        expected = 20 + (index * 17 % 105)
        capacity = next(int(room["capacity"]) for room in rooms if room["room_type"] == required_room and int(room["capacity"]) >= expected)
        approved = min(capacity, expected + 5) if index % 4 == 0 else ""
        initial = expected + 3 if not approved else ""
        scheduling = int(approved or initial or expected)
        weekly = 2 if two_meetings else 1
        rows.append({"course_code": f"SYN{index:04d}", "course_name": f"Môn tổng hợp {index:04d}", "section_code": f"SYN{index:04d}_01", "lecturer_code": f"GV{1 + ((index - 1) % lecturer_count):04d}", "required_sessions": str(30 if weekly == 2 else 15), "weekly_sessions": str(weekly), "periods_per_session": str(periods), "second_session_periods": str(second), "expected_students": str(expected), "initial_registration_limit": str(initial), "approved_max_students": str(approved), "scheduling_student_count": str(scheduling), "course_type": course_type, "required_room_type": required_room, "start_date": "2026-09-07", "end_date": "2026-12-20", "campus_code": "SYN", "notes": "Dữ liệu tổng hợp ẩn danh"})
    return rows


def _preferences(lecturers: list[dict[str, str]], slots: list[dict[str, str]]) -> list[dict[str, str]]:
    by_day = {int(slot["day_of_week"]): slot for slot in slots if slot["start_period"] == "1" and slot["end_period"] == "3"}
    return [{"lecturer_code": row["lecturer_code"], "slot_code": by_day[int(row["preferred_days"])]["slot_code"], "mandatory": "false", "reason": "Ưu tiên mềm tổng hợp"} for row in lecturers]


def _room_unavailability(rooms: list[dict[str, str]], slots: list[dict[str, str]], rng: random.Random) -> list[dict[str, str]]:
    candidates = [slot for slot in slots if slot["start_period"] == "1" and slot["end_period"] in {"3", "5", "6"}]
    return [{"room_code": room["room_code"], "slot_code": rng.choice(candidates)["slot_code"], "reason": "Bảo trì tổng hợp"} for room in rooms[::25]]


def _calendar() -> list[dict[str, str]]:
    start = date(2026, 9, 7)
    end = date(2027, 1, 10)
    rows = []
    current = start
    while current <= end:
        week = ((current - start).days // 7) + 1
        holiday = current == date(2026, 10, 20) or current == date(2026, 11, 20)
        rows.append({"date": current.isoformat(), "academic_week": str(week), "day_of_week": str(current.isoweekday() + 1), "is_teaching_day": "true", "is_holiday": str(holiday).lower(), "holiday_name": "Ngày nghỉ tổng hợp" if holiday else "", "note": "Synthetic scale fixture"})
        current += timedelta(days=1)
    return rows


def _write(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp/synthetic-scale"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lecturers", type=int, default=600)
    parser.add_argument("--sections", type=int, default=3000)
    parser.add_argument("--rooms", type=int, default=150)
    args = parser.parse_args()
    print(generate(args.output_dir, seed=args.seed, lecturers=args.lecturers, sections=args.sections, rooms=args.rooms))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
