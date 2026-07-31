from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260730_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("batch_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_import_batches_batch_code"), "import_batches", ["batch_code"], unique=True)

    op.create_table(
        "lecturers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lecturer_code", sa.String(length=50), nullable=False),
        sa.Column("lecturer_name", sa.String(length=255), nullable=False),
        sa.Column("preferred_days", sa.JSON(), nullable=False),
        sa.Column("preferred_slots", sa.JSON(), nullable=False),
        sa.Column("undesired_days", sa.JSON(), nullable=False),
        sa.Column("undesired_slots", sa.JSON(), nullable=False),
        sa.Column("max_days_per_week", sa.Integer(), nullable=True),
        sa.Column("max_consecutive_sessions", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lecturers_lecturer_code"), "lecturers", ["lecturer_code"], unique=True)

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_code", sa.String(length=50), nullable=False),
        sa.Column("room_name", sa.String(length=255), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("room_type", sa.String(length=50), nullable=False),
        sa.Column("room_size_category", sa.String(length=50), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rooms_room_code"), "rooms", ["room_code"], unique=True)

    op.create_table(
        "time_slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slot_code", sa.String(length=50), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_period", sa.Integer(), nullable=False),
        sa.Column("end_period", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(length=30), nullable=True),
        sa.Column("supports_course_types", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_time_slots_slot_code"), "time_slots", ["slot_code"], unique=True)

    op.create_table(
        "academic_terms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("term_code", sa.String(length=50), nullable=False),
        sa.Column("term_name", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_academic_terms_term_code"), "academic_terms", ["term_code"], unique=True)

    op.create_table(
        "academic_calendar_dates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("academic_week", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("is_teaching_day", sa.Boolean(), nullable=False),
        sa.Column("is_holiday", sa.Boolean(), nullable=False),
        sa.Column("holiday_name", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["term_id"], ["academic_terms.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("term_id", "date", name="uq_academic_calendar_dates_term_date"),
    )
    op.create_index(op.f("ix_academic_calendar_dates_date"), "academic_calendar_dates", ["date"], unique=False)

    op.create_table(
        "course_sections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("import_batch_id", sa.Integer(), nullable=True),
        sa.Column("course_code", sa.String(length=50), nullable=False),
        sa.Column("course_name", sa.String(length=255), nullable=False),
        sa.Column("section_code", sa.String(length=80), nullable=False),
        sa.Column("lecturer_id", sa.Integer(), nullable=False),
        sa.Column("required_sessions", sa.Integer(), nullable=False),
        sa.Column("weekly_sessions", sa.Integer(), nullable=False),
        sa.Column("periods_per_session", sa.Integer(), nullable=False),
        sa.Column("expected_students", sa.Integer(), nullable=False),
        sa.Column("initial_registration_limit", sa.Integer(), nullable=True),
        sa.Column("approved_max_students", sa.Integer(), nullable=True),
        sa.Column("scheduling_student_count", sa.Integer(), nullable=False),
        sa.Column("course_type", sa.String(length=30), nullable=False),
        sa.Column("required_room_type", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("campus_code", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"]),
        sa.ForeignKeyConstraint(["lecturer_id"], ["lecturers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_batch_id", "section_code", name="uq_course_sections_batch_section"),
    )
    op.create_index(op.f("ix_course_sections_section_code"), "course_sections", ["section_code"], unique=False)

    op.create_table(
        "ga_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_code", sa.String(length=50), nullable=False),
        sa.Column("import_batch_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("population_size", sa.Integer(), nullable=False),
        sa.Column("generations", sa.Integer(), nullable=False),
        sa.Column("mutation_rate", sa.Float(), nullable=True),
        sa.Column("crossover_rate", sa.Float(), nullable=True),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("best_fitness", sa.Float(), nullable=True),
        sa.Column("hard_violation_count", sa.Integer(), nullable=True),
        sa.Column("soft_cost", sa.Float(), nullable=True),
        sa.Column("soft_breakdown", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ga_runs_run_code"), "ga_runs", ["run_code"], unique=True)

    op.create_table(
        "schedule_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ga_run_id", sa.Integer(), nullable=False),
        sa.Column("course_section_id", sa.Integer(), nullable=False),
        sa.Column("lecturer_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("time_slot_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_section_id"], ["course_sections.id"]),
        sa.ForeignKeyConstraint(["ga_run_id"], ["ga_runs.id"]),
        sa.ForeignKeyConstraint(["lecturer_id"], ["lecturers.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.ForeignKeyConstraint(["time_slot_id"], ["time_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ga_run_id", "course_section_id", name="uq_schedule_assignments_run_section"),
    )

    op.create_table(
        "schedule_occurrences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("schedule_assignment_id", sa.Integer(), nullable=False),
        sa.Column("course_section_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("academic_week", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("time_slot_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_section_id"], ["course_sections.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.ForeignKeyConstraint(["schedule_assignment_id"], ["schedule_assignments.id"]),
        sa.ForeignKeyConstraint(["time_slot_id"], ["time_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("schedule_assignment_id", "date", name="uq_schedule_occurrences_assignment_date"),
    )


def downgrade() -> None:
    op.drop_table("schedule_occurrences")
    op.drop_table("schedule_assignments")
    op.drop_index(op.f("ix_ga_runs_run_code"), table_name="ga_runs")
    op.drop_table("ga_runs")
    op.drop_index(op.f("ix_course_sections_section_code"), table_name="course_sections")
    op.drop_table("course_sections")
    op.drop_index(op.f("ix_academic_calendar_dates_date"), table_name="academic_calendar_dates")
    op.drop_table("academic_calendar_dates")
    op.drop_index(op.f("ix_academic_terms_term_code"), table_name="academic_terms")
    op.drop_table("academic_terms")
    op.drop_index(op.f("ix_time_slots_slot_code"), table_name="time_slots")
    op.drop_table("time_slots")
    op.drop_index(op.f("ix_rooms_room_code"), table_name="rooms")
    op.drop_table("rooms")
    op.drop_index(op.f("ix_lecturers_lecturer_code"), table_name="lecturers")
    op.drop_table("lecturers")
    op.drop_index(op.f("ix_import_batches_batch_code"), table_name="import_batches")
    op.drop_table("import_batches")
