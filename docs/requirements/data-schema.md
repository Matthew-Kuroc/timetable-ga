# MVP Data Schema

This document defines the initial CSV contract for the MVP. It is based on `docs/requirements/SRS.md` and is intentionally small enough for early backend, GA and frontend work.

All CSV files must use UTF-8 encoding.

## 1. File List

| File | Purpose | Required for MVP |
| --- | --- | --- |
| `lecturers.csv` | Lecturer master data. | Yes |
| `rooms.csv` | Room master data. | Yes |
| `time_slots.csv` | Valid scheduling slots. | Yes |
| `course_sections.csv` | Course sections that need scheduling. | Yes |
| `lecturer_unavailable_slots.csv` | Mandatory lecturer unavailable slots. | Yes |
| `room_unavailable_slots.csv` | Room unavailable slots. | Should |

## 2. `lecturers.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `lecturer_code` | string | Yes | Unique, not blank. |
| `lecturer_name` | string | Yes | Display name. Use sample/fake names in repository data. |
| `preferred_slots` | string | No | Pipe-separated `slot_code` values, for example `MON_AM_01|WED_AM_01`. |
| `max_days_per_week` | integer | No | Desired value. Treated as soft until confirmed. |
| `max_consecutive_sessions` | integer | No | Desired value. Treated as soft until confirmed. |

## 3. `rooms.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `room_code` | string | Yes | Unique, not blank. |
| `room_name` | string | Yes | Display name. |
| `capacity` | integer | Yes | Greater than 0. |
| `room_type` | enum | Yes | `LY_THUYET` or `THUC_HANH` for MVP. |
| `campus_code` | string | Should | Optional for single-campus demos, but useful for future soft constraints. |
| `available` | boolean | Yes | `true` or `false`. |

## 4. `time_slots.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `slot_code` | string | Yes | Unique, not blank. |
| `day_of_week` | integer | Yes | 2 to 8, where 2 is Monday and 8 is Sunday. |
| `start_period` | integer | Yes | Greater than 0. |
| `end_period` | integer | Yes | Greater than or equal to `start_period`. |
| `session_type` | enum | Should | `SANG`, `CHIEU` or `TOI`. |
| `active` | boolean | Yes | `true` or `false`. |

## 5. `course_sections.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `course_code` | string | Yes | Not blank. |
| `course_name` | string | Yes | Not blank. |
| `section_code` | string | Yes | Unique within the dataset. |
| `lecturer_code` | string | Yes | Must exist in `lecturers.csv`. |
| `number_of_sessions` | integer | Yes | Greater than 0. |
| `periods_per_session` | integer | Yes | Greater than 0; usually 3 for theory classes. |
| `expected_students` | integer | Yes | Greater than 0. |
| `initial_registration_limit` | integer | No | Greater than 0 when present. |
| `approved_max_students` | integer | No | Greater than 0 when present. |
| `current_registered_students` | integer | No | Greater than or equal to 0 when present. |
| `scheduling_student_count` | integer | No | May be imported or computed. See capacity rule below. |
| `course_type` | enum | Yes | `LY_THUYET` or `THUC_HANH` for MVP. |
| `weeks` | string | Should | Range or list, for example `1-10` or `1,2,3,4`. |
| `campus_code` | string | No | Optional. |
| `notes` | string | No | Optional business note. |

## 6. `lecturer_unavailable_slots.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `lecturer_code` | string | Yes | Must exist in `lecturers.csv`. |
| `slot_code` | string | Yes | Must exist in `time_slots.csv`. |
| `weeks` | string | No | Empty means all weeks in the dataset. |
| `mandatory` | boolean | Yes | `true` means hard constraint. |
| `reason` | string | No | Optional note. |

## 7. `room_unavailable_slots.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `room_code` | string | Yes | Must exist in `rooms.csv`. |
| `slot_code` | string | Yes | Must exist in `time_slots.csv`. |
| `weeks` | string | No | Empty means all weeks in the dataset. |
| `reason` | string | No | Optional note. |

## 8. Capacity Rule

For the current draft, `scheduling_student_count` is computed as:

1. `approved_max_students`, if present.
2. Otherwise `initial_registration_limit`, if present.
3. Otherwise `expected_students`.

Room capacity must be greater than or equal to `scheduling_student_count`.

This rule is documented in the SRS draft, but the final production rule should still be confirmed with the supervisor and kept centralized in implementation.

## 9. Week Format

The MVP accepts:

- A range: `1-10`
- A comma-separated list: `1,3,5,7`
- Empty value where the surrounding context defines all active weeks.

Implementation should normalize this into a list of integers before GA or conflict checking.

