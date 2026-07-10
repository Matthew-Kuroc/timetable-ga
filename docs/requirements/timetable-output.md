# Timetable Output Contract

This document defines the output produced by the GA module and consumed by backend APIs, frontend views and export logic.

## 1. Timetable Session Fields

Each scheduled session should have these fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `run_code` | string | Yes | GA run or timetable option code. |
| `session_id` | string | Yes | Unique generated session ID. |
| `section_code` | string | Yes | Course-section code. |
| `course_code` | string | Yes | Course code. |
| `course_name` | string | Yes | Course name. |
| `lecturer_code` | string | Yes | Lecturer code. |
| `lecturer_name` | string | Yes | Lecturer display name. |
| `room_code` | string | Yes | Assigned room code. |
| `room_name` | string | Yes | Assigned room display name. |
| `slot_code` | string | Yes | Assigned time slot code. |
| `day_of_week` | integer | Yes | 2 to 8, where 2 is Monday and 8 is Sunday. |
| `start_period` | integer | Yes | Start period. |
| `end_period` | integer | Yes | End period. |
| `week` | integer | Yes | Teaching week number. |
| `course_type` | enum | Yes | `LY_THUYET` or `THUC_HANH` for MVP. |
| `scheduling_student_count` | integer | Yes | Student count used for capacity checking. |
| `status` | enum | Yes | `SCHEDULED`, `SUSPENDED` or `MOVED`. |

## 2. Run Metrics Fields

GA run summary should include:

| Field | Type | Description |
| --- | --- | --- |
| `run_code` | string | Unique run code. |
| `dataset_code` | string | Input dataset batch used by the run. |
| `status` | enum | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED` or `STOPPED`. |
| `population_size` | integer | GA population size. |
| `generations` | integer | Number of generations configured. |
| `crossover_rate` | number | 0 to 1. |
| `mutation_rate` | number | 0 to 1. |
| `seed` | integer | Optional reproducibility seed. |
| `fitness` | number | Best fitness score. |
| `hard_violation_count` | integer | Must be 0 for a valid selected timetable. |
| `soft_violation_count` | integer | Total soft violations or weighted soft penalty count. |
| `started_at` | datetime | Run start time. |
| `finished_at` | datetime | Run finish time. |
| `duration_seconds` | number | Runtime duration. |

## 3. Violation Report Fields

Validation and GA checking should report violations in this shape:

| Field | Type | Description |
| --- | --- | --- |
| `code` | string | Constraint code, for example `HC-01` or `SC-01`. |
| `severity` | enum | `HARD` or `SOFT`. |
| `message` | string | Human-readable Vietnamese message in UI. |
| `session_id` | string | Related session if available. |
| `section_code` | string | Related course section if available. |
| `lecturer_code` | string | Related lecturer if available. |
| `room_code` | string | Related room if available. |
| `slot_code` | string | Related time slot if available. |
| `week` | integer | Related week if available. |

## 4. View Support

The output contract supports:

- Lecturer view by filtering `lecturer_code`.
- Room view by filtering `room_code`.
- Course-section view by filtering `section_code`.
- Weekly view by filtering `week`.
- Export by reusing the same session fields.

## 5. Output Validity

A timetable can be selected as valid only when:

- `hard_violation_count` is 0.
- Every session has section, lecturer, room, slot and week.
- Every course section has the required number of sessions.
- All generated sessions pass `HC-01` to `HC-12`.

