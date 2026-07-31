# Timetable Output Contract

This document defines output produced by the GA module and consumed by backend APIs, frontend views and export logic.

The MVP GA output is a base weekly assignment per course section. Dated session occurrences are generated later by a calendar-expansion service.

## 1. Base Assignment Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `run_code` | string | Yes | GA run code. |
| `section_code` | string | Yes | Course-section code. |
| `course_code` | string | Yes | Course code. |
| `course_name` | string | Yes | Course name. |
| `lecturer_code` | string | Yes | Fixed primary lecturer code. |
| `lecturer_name` | string | Yes | Lecturer display name. |
| `room_code` | string | Yes | Assigned room code. |
| `room_name` | string | Yes | Assigned room display name. |
| `slot_code` | string | Yes | Assigned configured time slot. |
| `day_of_week` | integer | Yes | `2` to `8`, Monday to Sunday. |
| `start_period` | integer | Yes | Start period. |
| `end_period` | integer | Yes | End period. |
| `course_type` | enum | Yes | `THEORY`, `PRACTICE`, `INTEGRATED`. |
| `required_room_type` | enum/string | Yes | Required room type from the course section. |
| `scheduling_student_count` | integer | Yes | Student count used for capacity checking. |
| `status` | enum | Yes | Example: `SCHEDULED`, `MOVED`, `CANCELLED`. |

## 2. Dated Occurrence Fields

When the academic calendar expands a base assignment into actual dates, each occurrence should include:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `occurrence_id` | string | Yes | Unique generated occurrence ID. |
| `section_code` | string | Yes | Course-section code. |
| `date` | date | Yes | Teaching date. |
| `academic_week` | integer | Yes | Academic week number. |
| `room_code` | string | Yes | Effective room for this occurrence. |
| `slot_code` | string | Yes | Effective slot for this occurrence. |
| `status` | enum | Yes | Example: `SCHEDULED`, `MOVED`, `MAKEUP`. |

When a regular class date falls on a holiday or non-teaching day, do not generate a normal occurrence for that date, do not show it as `SUSPENDED`, and do not automatically move it. The course section may be reported as needing a makeup session later.

## 3. Run Metrics Fields

| Field | Type | Description |
| --- | --- | --- |
| `run_code` | string | Unique run code. |
| `dataset_code` | string | Import batch used by the run. |
| `status` | enum | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `STOPPED`. |
| `population_size` | integer | GA population size. |
| `generations` | integer | Maximum generations configured. |
| `crossover_rate` | number | 0 to 1 when real crossover is implemented. |
| `mutation_rate` | number | 0 to 1 when real mutation is implemented. |
| `seed` | integer | Reproducibility seed. |
| `hard_violation_count` | integer | Must be 0 for a selectable timetable. |
| `soft_cost` | number | Weighted soft cost. |
| `soft_breakdown` | object | Explanation of soft cost components. |
| `started_at` | datetime | Run start time. |
| `finished_at` | datetime | Run finish time. |
| `duration_seconds` | number | Runtime duration. |

## 4. Violation Report Fields

| Field | Type | Description |
| --- | --- | --- |
| `code` | string | Constraint code, for example `HC-01`. |
| `severity` | enum | `HARD` or `SOFT`. |
| `message` | string | Human-readable Vietnamese message in UI. |
| `section_code` | string | Related section when available. |
| `other_section_code` | string | Second section for overlap conflicts when available. |
| `lecturer_code` | string | Related lecturer when available. |
| `room_code` | string | Related room when available. |
| `slot_code` | string | Related slot when available. |

## 5. View Support

The output supports:

- Lecturer view by filtering `lecturer_code`.
- Room view by filtering `room_code`.
- Course-section view by filtering `section_code`.
- Weekly view after calendar expansion.
- CSV/Excel export using the same base assignment or occurrence fields.

## 6. Output Validity

A timetable can be selected as valid only when:

- `hard_violation_count` is 0.
- Every course section has exactly one base assignment in the MVP.
- Every assignment has section, lecturer, room and active configured slot.
- All hard constraints pass.
