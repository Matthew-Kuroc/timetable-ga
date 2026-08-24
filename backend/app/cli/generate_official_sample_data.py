from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path


LECTURERS = (
    ("GV001", "Nguyễn Văn An"),
    ("GV002", "Trần Thị Bình"),
    ("GV003", "Lê Minh Châu"),
    ("GV004", "Phạm Quốc Dũng"),
    ("GV005", "Hoàng Thị Hạnh"),
    ("GV006", "Võ Anh Khoa"),
    ("GV007", "Đặng Thanh Lan"),
    ("GV008", "Bùi Đức Long"),
    ("GV009", "Đỗ Thị Mai"),
    ("GV010", "Huỳnh Gia Nam"),
    ("GV011", "Ngô Phương Nhi"),
    ("GV012", "Mai Tiến Phát"),
    ("GV013", "Cao Thu Quỳnh"),
    ("GV014", "Lý Hoàng Sơn"),
    ("GV015", "Tạ Minh Tâm"),
    ("GV016", "Đinh Bảo Trâm"),
    ("GV017", "Phan Nhật Vũ"),
    ("GV018", "Hồ Khánh Vy"),
    ("GV019", "Trương Quốc Việt"),
    ("GV020", "Vũ Kim Yến"),
)

COURSES = (
    ("IT101", "Nhập môn lập trình", "THEORY", "THEORY_ROOM", 3),
    ("IT102", "Kỹ thuật lập trình", "PRACTICE", "COMPUTER_LAB", 5),
    ("IT103", "Cấu trúc dữ liệu và giải thuật", "THEORY", "THEORY_ROOM", 3),
    ("IT104", "Cơ sở dữ liệu", "INTEGRATED", "COMPUTER_LAB", 5),
    ("IT105", "Hệ quản trị cơ sở dữ liệu", "PRACTICE", "COMPUTER_LAB", 6),
    ("IT106", "Mạng máy tính", "THEORY", "THEORY_ROOM", 3),
    ("IT107", "An toàn thông tin", "THEORY", "THEORY_ROOM", 3),
    ("IT108", "Phân tích thiết kế hệ thống", "THEORY", "THEORY_ROOM", 3),
    ("IT109", "Công nghệ phần mềm", "INTEGRATED", "COMPUTER_LAB", 5),
    ("IT110", "Kiểm thử phần mềm", "PRACTICE", "COMPUTER_LAB", 5),
    ("IT111", "Lập trình web", "INTEGRATED", "COMPUTER_LAB", 5),
    ("IT112", "Phát triển ứng dụng di động", "PRACTICE", "COMPUTER_LAB", 6),
    ("IT113", "Trí tuệ nhân tạo", "THEORY", "THEORY_ROOM", 3),
    ("IT114", "Học máy", "INTEGRATED", "COMPUTER_LAB", 5),
    ("IT115", "Khai phá dữ liệu", "THEORY", "THEORY_ROOM", 3),
    ("IT116", "Điện toán đám mây", "THEORY", "THEORY_ROOM", 3),
    ("IT117", "DevOps và triển khai phần mềm", "PRACTICE", "COMPUTER_LAB", 5),
    ("IT118", "Thiết kế giao diện người dùng", "INTEGRATED", "COMPUTER_LAB", 5),
    ("IT119", "Hệ điều hành", "THEORY", "THEORY_ROOM", 3),
    ("IT120", "Kiến trúc máy tính", "THEORY", "THEORY_ROOM", 3),
    ("IT121", "Xử lý ảnh số", "PRACTICE", "SPECIALIZED_LAB", 5),
    ("IT122", "Internet vạn vật", "INTEGRATED", "SPECIALIZED_LAB", 6),
    ("IT123", "Phân tích dữ liệu kinh doanh", "THEORY", "THEORY_ROOM", 3),
    ("IT124", "Quản lý dự án phần mềm", "THEORY", "THEORY_ROOM", 3),
)

DAY_PREFIXES = {2: "MON", 3: "TUE", 4: "WED", 5: "THU", 6: "FRI", 7: "SAT", 8: "SUN"}
THEORY_RANGES = ((1, 3), (4, 6), (7, 9), (10, 12), (13, 15))
LONG_RANGES = ((1, 5), (1, 6), (2, 6))


def main() -> int:
    output_dir = Path("data/samples/official")
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_lecturers(output_dir)
    _write_rooms(output_dir)
    _write_time_slots(output_dir)
    _write_course_sections(output_dir, section_count=120)
    _write_lecturer_time_preferences(output_dir)
    _write_room_unavailable_slots(output_dir)
    _write_academic_calendar(output_dir)
    return 0


def _write_lecturers(output_dir: Path) -> None:
    rows = []
    for index, (lecturer_code, lecturer_name) in enumerate(LECTURERS):
        first_day = 2 + index % 7
        second_day = 2 + (index + 2) % 7
        undesired_day = 2 + (index + 4) % 7
        preferred_slots = f"{DAY_PREFIXES[first_day]}_1_3|{DAY_PREFIXES[second_day]}_4_6"
        rows.append(
            {
                "lecturer_code": lecturer_code,
                "lecturer_name": lecturer_name,
                "preferred_days": f"{first_day}|{second_day}",
                "preferred_slots": preferred_slots,
                "undesired_days": str(undesired_day),
                "undesired_slots": f"{DAY_PREFIXES[undesired_day]}_13_15",
                "max_days_per_week": "4",
                "max_consecutive_sessions": "3",
            }
        )
    _write_csv(output_dir / "lecturers.csv", rows)


def _write_rooms(output_dir: Path) -> None:
    rows = []
    for floor in range(2, 7):
        for number in range(1, 4):
            rows.append(_room(f"A{floor}{number:02d}", f"Phòng lý thuyết A{floor}{number:02d}", 60, "THEORY_ROOM", "STANDARD"))
    for number in range(1, 5):
        rows.append(_room(f"H{number:02d}", f"Giảng đường lớn H{number:02d}", 130, "THEORY_ROOM", "LARGE_HALL"))
    for floor in range(3, 6):
        for number in range(1, 4):
            rows.append(_room(f"LAB{floor}{number:02d}", f"Phòng máy LAB{floor}{number:02d}", 50, "COMPUTER_LAB", "STANDARD"))
    for number in range(1, 4):
        rows.append(_room(f"SP{number:02d}", f"Phòng thực hành chuyên ngành SP{number:02d}", 45, "SPECIALIZED_LAB", "STANDARD"))
    _write_csv(output_dir / "rooms.csv", rows)


def _room(room_code: str, room_name: str, capacity: int, room_type: str, category: str) -> dict[str, str]:
    return {
        "room_code": room_code,
        "room_name": room_name,
        "capacity": str(capacity),
        "room_type": room_type,
        "room_size_category": category,
        "available": "true",
    }


def _write_time_slots(output_dir: Path) -> None:
    rows = []
    for day, prefix in DAY_PREFIXES.items():
        for start, end in THEORY_RANGES:
            rows.append(
                {
                    "slot_code": f"{prefix}_{start}_{end}",
                    "day_of_week": str(day),
                    "start_period": str(start),
                    "end_period": str(end),
                    "session_type": "SANG" if end <= 6 else "CHIEU" if end <= 12 else "TOI",
                    "supports_course_types": "THEORY",
                    "active": "true",
                }
            )
        for start, end in LONG_RANGES:
            rows.append(
                {
                    "slot_code": f"{prefix}_{start}_{end}",
                    "day_of_week": str(day),
                    "start_period": str(start),
                    "end_period": str(end),
                    "session_type": "SANG",
                    "supports_course_types": "PRACTICE|INTEGRATED",
                    "active": "true",
                }
            )
    _write_csv(output_dir / "time_slots.csv", rows)


def _write_course_sections(output_dir: Path, section_count: int) -> None:
    rows = []
    for index in range(section_count):
        course_code, course_name, course_type, room_type, periods = COURSES[index % len(COURSES)]
        section_number = index // len(COURSES) + 1
        expected_students = _expected_students(index, room_type)
        initial_limit = min(expected_students + 5, 60 if room_type == "THEORY_ROOM" else 50)
        approved_max = "" if index % 5 else str(initial_limit)
        scheduling_count = int(approved_max or initial_limit or expected_students)
        if course_code in {"IT113", "IT120", "IT123"} and course_type == "THEORY":
            scheduling_count = 100
            initial_limit = 100
            approved_max = ""
        rows.append(
            {
                "course_code": course_code,
                "course_name": course_name,
                "section_code": f"{course_code}_{section_number:02d}",
                "lecturer_code": LECTURERS[index % len(LECTURERS)][0],
                "required_sessions": "15",
                "weekly_sessions": "1",
                "periods_per_session": str(periods),
                "second_session_periods": "",
                "expected_students": str(expected_students),
                "initial_registration_limit": str(initial_limit),
                "approved_max_students": approved_max,
                "scheduling_student_count": str(scheduling_count),
                "course_type": course_type,
                "required_room_type": room_type,
                "start_date": "2026-09-07",
                "end_date": "2026-12-20",
                "campus_code": "CS1",
                "notes": "",
            }
        )
    _write_csv(output_dir / "course_sections.csv", rows)


def _expected_students(index: int, room_type: str) -> int:
    if room_type == "SPECIALIZED_LAB":
        return 32 + index % 8
    if room_type == "COMPUTER_LAB":
        return 35 + index % 10
    return 45 + index % 12


def _write_lecturer_time_preferences(output_dir: Path) -> None:
    rows = []
    for index, (lecturer_code, _lecturer_name) in enumerate(LECTURERS):
        undesired_day = 2 + (index + 4) % 7
        rows.append(
            {
                "lecturer_code": lecturer_code,
                "slot_code": f"{DAY_PREFIXES[undesired_day]}_13_15",
                "mandatory": "false",
                "reason": "Không ưu tiên dạy ca tối",
            }
        )
        if index % 5 == 0:
            rows.append(
                {
                    "lecturer_code": lecturer_code,
                    "slot_code": f"{DAY_PREFIXES[2 + index % 7]}_7_9",
                    "mandatory": "true",
                    "reason": "Lịch họp cố định đã được Phòng đào tạo xác nhận",
                }
            )
    _write_csv(output_dir / "lecturer_time_preferences.csv", rows)


def _write_room_unavailable_slots(output_dir: Path) -> None:
    rows = (
        {"room_code": "LAB301", "slot_code": "MON_1_5", "reason": "Bảo trì định kỳ"},
        {"room_code": "LAB402", "slot_code": "WED_1_6", "reason": "Cài đặt phần mềm"},
        {"room_code": "SP01", "slot_code": "FRI_2_6", "reason": "Bảo trì thiết bị"},
        {"room_code": "H01", "slot_code": "SUN_13_15", "reason": "Không mở ca tối Chủ nhật"},
    )
    _write_csv(output_dir / "room_unavailable_slots.csv", rows)


def _write_academic_calendar(output_dir: Path) -> None:
    rows = []
    start_date = date(2026, 9, 7)
    holidays = {
        date(2026, 9, 14): ("Ngày nghỉ học kỳ", "Không sinh buổi học bình thường"),
        date(2026, 11, 20): ("Ngày Nhà giáo Việt Nam", "Không sinh buổi học bình thường"),
        date(2026, 12, 7): ("Tuần dự phòng thi", "Không sinh buổi học bình thường"),
    }
    for offset in range(18 * 7):
        current = start_date + timedelta(days=offset)
        academic_week = offset // 7 + 1
        day_of_week = current.weekday() + 2
        holiday = holidays.get(current)
        rows.append(
            {
                "date": current.isoformat(),
                "academic_week": str(academic_week),
                "day_of_week": str(day_of_week),
                "is_teaching_day": "false" if holiday else "true",
                "is_holiday": "true" if holiday else "false",
                "holiday_name": holiday[0] if holiday else "",
                "note": holiday[1] if holiday else "",
            }
        )
    _write_csv(output_dir / "academic_calendar.csv", rows)


def _write_csv(path: Path, rows: list[dict[str, str]] | tuple[dict[str, str], ...]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
