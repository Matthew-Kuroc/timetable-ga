from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum
from backend.app.db.base import Base


class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    semester: Mapped[str | None] = mapped_column(String(50))
    academic_year: Mapped[str | None] = mapped_column(String(30))
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="UPLOADED")
    note: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    course_sections: Mapped[list[CourseSectionModel]] = relationship(back_populates="import_batch")
    ga_runs: Mapped[list[GaRunModel]] = relationship(back_populates="import_batch")


class LecturerModel(Base):
    __tablename__ = "lecturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lecturer_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    lecturer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_days: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    preferred_slots: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    undesired_days: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    undesired_slots: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    max_days_per_week: Mapped[int | None] = mapped_column(Integer)
    max_consecutive_sessions: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    course_sections: Mapped[list[CourseSectionModel]] = relationship(back_populates="lecturer")


class RoomModel(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    room_name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    room_size_category: Mapped[str] = mapped_column(String(50), nullable=False, default="STANDARD")
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    schedule_assignments: Mapped[list[ScheduleAssignmentModel]] = relationship(back_populates="room")


class TimeSlotModel(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slot_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_period: Mapped[int] = mapped_column(Integer, nullable=False)
    end_period: Mapped[int] = mapped_column(Integer, nullable=False)
    session_type: Mapped[str | None] = mapped_column(String(30))
    supports_course_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    schedule_assignments: Mapped[list[ScheduleAssignmentModel]] = relationship(back_populates="time_slot")


class AcademicTermModel(Base):
    __tablename__ = "academic_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    term_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    calendar_dates: Mapped[list[AcademicCalendarDateModel]] = relationship(back_populates="term")


class AcademicCalendarDateModel(Base):
    __tablename__ = "academic_calendar_dates"
    __table_args__ = (
        UniqueConstraint("term_id", "date", name="uq_academic_calendar_dates_term_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term_id: Mapped[int | None] = mapped_column(ForeignKey("academic_terms.id"))
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    academic_week: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    is_teaching_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    holiday_name: Mapped[str | None] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    term: Mapped[AcademicTermModel | None] = relationship(back_populates="calendar_dates")


class CourseSectionModel(Base):
    __tablename__ = "course_sections"
    __table_args__ = (
        UniqueConstraint("import_batch_id", "section_code", name="uq_course_sections_batch_section"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.id"))
    course_code: Mapped[str] = mapped_column(String(50), nullable=False)
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    lecturer_id: Mapped[int] = mapped_column(ForeignKey("lecturers.id"), nullable=False)
    required_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    weekly_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    periods_per_session: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_students: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_registration_limit: Mapped[int | None] = mapped_column(Integer)
    approved_max_students: Mapped[int | None] = mapped_column(Integer)
    scheduling_student_count: Mapped[int] = mapped_column(Integer, nullable=False)
    course_type: Mapped[str] = mapped_column(String(30), nullable=False)
    required_room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    campus_code: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    import_batch: Mapped[ImportBatchModel | None] = relationship(back_populates="course_sections")
    lecturer: Mapped[LecturerModel] = relationship(back_populates="course_sections")
    schedule_assignments: Mapped[list[ScheduleAssignmentModel]] = relationship(back_populates="course_section")


class GaRunModel(Base):
    __tablename__ = "ga_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    import_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.id"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    population_size: Mapped[int] = mapped_column(Integer, nullable=False)
    generations: Mapped[int] = mapped_column(Integer, nullable=False)
    mutation_rate: Mapped[float | None]
    crossover_rate: Mapped[float | None]
    seed: Mapped[int | None] = mapped_column(Integer)
    best_fitness: Mapped[float | None]
    hard_violation_count: Mapped[int | None] = mapped_column(Integer)
    soft_cost: Mapped[float | None]
    soft_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    import_batch: Mapped[ImportBatchModel | None] = relationship(back_populates="ga_runs")
    schedule_assignments: Mapped[list[ScheduleAssignmentModel]] = relationship(back_populates="ga_run")
    official_timetables: Mapped[list[OfficialTimetableModel]] = relationship(back_populates="source_ga_run")


class DatasetSnapshotModel(Base):
    __tablename__ = "dataset_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    parent_batch_code: Mapped[str | None] = mapped_column(String(50))
    snapshot_path: Mapped[str] = mapped_column(Text, nullable=False)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ScheduleChangeLogModel(Base):
    __tablename__ = "schedule_change_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_code: Mapped[str | None] = mapped_column(String(50), index=True)
    official_code: Mapped[str | None] = mapped_column(String(50), index=True)
    section_code: Mapped[str] = mapped_column(String(80), nullable=False)
    scope: Mapped[str] = mapped_column(String(40), nullable=False)
    previous_value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    current_value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    changed_by: Mapped[str] = mapped_column(String(80), nullable=False, default="training_office")
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class OfficialTimetableModel(Base):
    __tablename__ = "official_timetables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    official_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    source_ga_run_id: Mapped[int] = mapped_column(ForeignKey("ga_runs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PUBLISHED")
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    source_ga_run: Mapped[GaRunModel] = relationship(back_populates="official_timetables")
    segments: Mapped[list[ScheduleSegmentModel]] = relationship(back_populates="official_timetable", cascade="all, delete-orphan")
    makeup_sessions: Mapped[list[MakeupSessionModel]] = relationship(back_populates="official_timetable", cascade="all, delete-orphan")


class ScheduleSegmentModel(Base):
    __tablename__ = "schedule_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    official_timetable_id: Mapped[int] = mapped_column(ForeignKey("official_timetables.id"), nullable=False, index=True)
    section_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    room_code: Mapped[str] = mapped_column(String(50), nullable=False)
    slot_code: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    official_timetable: Mapped[OfficialTimetableModel] = relationship(back_populates="segments")


class MakeupSessionModel(Base):
    __tablename__ = "makeup_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    official_timetable_id: Mapped[int] = mapped_column(ForeignKey("official_timetables.id"), nullable=False, index=True)
    section_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    original_missing_date: Mapped[date | None] = mapped_column(Date)
    makeup_date: Mapped[date] = mapped_column(Date, nullable=False)
    academic_week: Mapped[int] = mapped_column(Integer, nullable=False)
    room_code: Mapped[str] = mapped_column(String(50), nullable=False)
    slot_code: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    official_timetable: Mapped[OfficialTimetableModel] = relationship(back_populates="makeup_sessions")


class ScheduleAssignmentModel(Base):
    __tablename__ = "schedule_assignments"
    __table_args__ = (
        UniqueConstraint("ga_run_id", "course_section_id", name="uq_schedule_assignments_run_section"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ga_run_id: Mapped[int] = mapped_column(ForeignKey("ga_runs.id"), nullable=False)
    course_section_id: Mapped[int] = mapped_column(ForeignKey("course_sections.id"), nullable=False)
    lecturer_id: Mapped[int] = mapped_column(ForeignKey("lecturers.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SCHEDULED")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    ga_run: Mapped[GaRunModel] = relationship(back_populates="schedule_assignments")
    course_section: Mapped[CourseSectionModel] = relationship(back_populates="schedule_assignments")
    lecturer: Mapped[LecturerModel] = relationship()
    room: Mapped[RoomModel] = relationship(back_populates="schedule_assignments")
    time_slot: Mapped[TimeSlotModel] = relationship(back_populates="schedule_assignments")
    occurrences: Mapped[list[ScheduleOccurrenceModel]] = relationship(back_populates="schedule_assignment")


class ScheduleOccurrenceModel(Base):
    __tablename__ = "schedule_occurrences"
    __table_args__ = (
        UniqueConstraint("schedule_assignment_id", "date", name="uq_schedule_occurrences_assignment_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_assignment_id: Mapped[int] = mapped_column(ForeignKey("schedule_assignments.id"), nullable=False)
    course_section_id: Mapped[int] = mapped_column(ForeignKey("course_sections.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    academic_week: Mapped[int] = mapped_column(Integer, nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SCHEDULED")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    schedule_assignment: Mapped[ScheduleAssignmentModel] = relationship(back_populates="occurrences")
    course_section: Mapped[CourseSectionModel] = relationship()
    room: Mapped[RoomModel] = relationship()
    time_slot: Mapped[TimeSlotModel] = relationship()
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TRAINING_OFFICE = "TRAINING_OFFICE"
    LECTURER = "LECTURER"

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    lecturer_code: Mapped[str | None] = mapped_column(String(50))