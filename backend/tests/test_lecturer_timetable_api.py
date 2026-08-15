from __future__ import annotations

from datetime import date, datetime, timezone

from backend.app.db.models import GaRunModel, OfficialTimetableModel, TimeSlotModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.tests.auth_helpers import authenticated_client


def test_lecturer_sees_only_owned_occurrences_with_effective_slot_details() -> None:
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        session.add_all(
            [
                TimeSlotModel(
                    slot_code="MON_1_3",
                    day_of_week=2,
                    start_period=1,
                    end_period=3,
                    supports_course_types=["THEORY"],
                    active=True,
                ),
                TimeSlotModel(
                    slot_code="MON_4_6",
                    day_of_week=2,
                    start_period=4,
                    end_period=6,
                    supports_course_types=["THEORY"],
                    active=True,
                ),
            ]
        )
        run = GaRunModel(
            run_code="RUN-OWNERSHIP",
            status="COMPLETED",
            population_size=10,
            generations=1,
            payload={},
            created_at=now,
        )
        session.add(run)
        session.flush()
        payload = {
            "official_code": "OFFICIAL-OWNERSHIP",
            "assignments": [
                {
                    "section_code": "SEC-A",
                    "course_code": "COURSE-A",
                    "course_name": "Môn A",
                    "lecturer_code": "GV001",
                    "lecturer_name": "Giảng viên Một",
                    "room_code": "A101",
                    "slot_code": "MON_1_3",
                    "day_of_week": 2,
                    "start_period": 1,
                    "end_period": 3,
                    "course_type": "THEORY",
                },
                {
                    "section_code": "SEC-B",
                    "course_code": "COURSE-B",
                    "course_name": "Môn B",
                    "lecturer_code": "GV002",
                    "lecturer_name": "Giảng viên Hai",
                    "room_code": "B201",
                    "slot_code": "MON_1_3",
                    "day_of_week": 2,
                    "start_period": 1,
                    "end_period": 3,
                    "course_type": "THEORY",
                },
            ],
            "occurrences": [
                {
                    "section_code": "SEC-A",
                    "date": date(2026, 8, 10).isoformat(),
                    "academic_week": 1,
                    "room_code": "A102",
                    "slot_code": "MON_4_6",
                    "status": "EXCEPTION",
                },
                {
                    "section_code": "SEC-B",
                    "date": date(2026, 8, 10).isoformat(),
                    "academic_week": 1,
                    "room_code": "B201",
                    "slot_code": "MON_1_3",
                    "status": "SCHEDULED",
                },
            ],
        }
        session.add(
            OfficialTimetableModel(
                official_code="OFFICIAL-OWNERSHIP",
                source_ga_run_id=run.id,
                status="PUBLISHED",
                version_number=1,
                payload=payload,
                published_at=now,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    lecturer = authenticated_client(
        UserRole.LECTURER,
        username="gv001",
        lecturer_code="GV001",
    )
    response = lecturer.get("/api/lecturer/timetable", params={"week": 1})

    assert response.status_code == 200
    result = response.json()
    assert {item["section_code"] for item in result["occurrences"]} == {"SEC-A"}
    assert {item["section_code"] for item in result["course_sections"]} == {"SEC-A"}
    occurrence = result["occurrences"][0]
    assert occurrence["room_code"] == "A102"
    assert occurrence["slot_code"] == "MON_4_6"
    assert occurrence["start_period"] == 4
    assert occurrence["end_period"] == 6
    assert occurrence["day_of_week"] == date(2026, 8, 10).isoweekday() + 1

