# MVP Data Schema

This document defines the CSV dataset used by the MVP backend, GA module and early frontend work. It follows the updated UR/SRS and repository `AGENTS.md`.

All CSV files must use UTF-8 encoding. Vietnamese display values are allowed and must be preserved.

## 1. Dataset Files

The application imports a dataset batch, not a single isolated CSV file.

The Training Department prepares all seven files in Excel, uploads them as one
batch, reviews the validation result, and explicitly confirms the batch before
running GA. Each confirmed batch must be versioned or snapshotted so a later
upload cannot alter a previous GA run. `data/samples/official` is only a
development and demonstration fixture, never the normal runtime input source.

| File | Purpose | Required |
| --- | --- | --- |
| `lecturers.csv` | Lecturer master data and soft preferences. | Yes |
| `rooms.csv` | Room master data. | Yes |
| `time_slots.csv` | Configured valid time slots. | Yes |
| `course_sections.csv` | Course sections that need scheduling. | Yes |
| `lecturer_time_preferences.csv` | Lecturer preferred, undesired, or officially confirmed restricted slots. | Yes |
| `room_unavailable_slots.csv` | Room unavailable slots. | Yes |
| `academic_calendar.csv` | Academic dates, teaching days and holidays used after base timetable generation. | Yes |

## 2. `lecturers.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `lecturer_code` | string | Yes | Unique, not blank. |
| `lecturer_name` | string | Yes | Display name. Sample data must be fake or anonymized. |
| `preferred_days` | string | No | Pipe-separated day numbers, `2` to `8`. |
| `preferred_slots` | string | No | Pipe-separated `slot_code` values. |
| `undesired_days` | string | No | Pipe-separated day numbers, soft constraint. |
| `undesired_slots` | string | No | Pipe-separated `slot_code` values, soft constraint. |
| `max_days_per_week` | integer | No | Desired value, treated as soft unless confirmed otherwise. |
| `max_consecutive_sessions` | integer | No | Desired value, treated as soft unless confirmed otherwise. |

## 3. `rooms.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `room_code` | string | Yes | Unique, not blank. |
| `room_name` | string | Yes | Display name. |
| `capacity` | integer | Yes | Greater than 0. |
| `room_type` | enum | Yes | `THEORY_ROOM`, `COMPUTER_LAB`, `SPECIALIZED_LAB`. |
| `room_size_category` | enum/string | Yes | Example: `STANDARD`, `LARGE_HALL`. Large rooms remain valid for compatible sections. |
| `available` | boolean | Yes | `true` or `false`. |

## 4. `time_slots.csv`

The GA must only use configured valid time slots.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `slot_code` | string | Yes | Unique, not blank. |
| `day_of_week` | integer | Yes | `2` to `8`, where `2` is Monday and `8` is Sunday. |
| `start_period` | integer | Yes | Start period. |
| `end_period` | integer | Yes | End period. |
| `session_type` | enum/string | Yes | Example: `SANG`, `CHIEU`, `TOI`. |
| `supports_course_types` | string | Yes | Pipe-separated values from `THEORY`, `PRACTICE`, `INTEGRATED`. |
| `active` | boolean | Yes | `true` or `false`. |

Valid slot ranges:

| Course type | Valid period ranges |
| --- | --- |
| `THEORY` | `1-3`, `4-6`, `7-9`, `10-12`, `13-15` |
| `PRACTICE` | `1-5`, `1-6`, `2-6` |
| `INTEGRATED` | `1-5`, `1-6`, `2-6` |

Saturday and Sunday are valid teaching days when configured. An evening,
Saturday, or Sunday slot may receive a configurable soft avoidance cost during
GA scoring, but is never invalid solely for that reason.

## 5. `course_sections.csv`

Teaching assignments are fixed input data. The GA does not choose lecturers.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `course_code` | string | Yes | Not blank. |
| `course_name` | string | Yes | Not blank. Vietnamese text is allowed. |
| `section_code` | string | Yes | Unique within the dataset batch. |
| `lecturer_code` | string | Yes | Must exist in `lecturers.csv`. |
| `required_sessions` | integer | Yes | Required number of semester sessions, normally about 15. |
| `weekly_sessions` | integer | Yes | MVP value is normally `1`. |
| `periods_per_session` | integer | Yes | `3` for theory, `5` or `6` for practice/integrated. |
| `expected_students` | integer | Yes | Greater than 0. |
| `initial_registration_limit` | integer | No | Greater than 0 when present. |
| `approved_max_students` | integer | No | Greater than 0 when present. |
| `scheduling_student_count` | integer | Yes | Must follow the capacity priority rule below. |
| `course_type` | enum | Yes | `THEORY`, `PRACTICE`, `INTEGRATED`. |
| `required_room_type` | enum/string | Yes | Must be satisfied by `rooms.room_type`. |
| `start_date` | date | Yes | ISO date `YYYY-MM-DD`. |
| `end_date` | date | Yes | ISO date `YYYY-MM-DD`. |
| `campus_code` | string | No | Optional. No travel-time constraint is added. |
| `notes` | string | No | Optional business note. |

Capacity priority:

```text
scheduling_student_count =
  approved_max_students
  else initial_registration_limit
  else expected_students
```

## 6. `lecturer_time_preferences.csv`

This file records lecturer time preferences before course registration. Rows are soft constraints by default. A row is a hard restriction only when the Training Office has officially confirmed that the lecturer cannot be scheduled in that slot.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `lecturer_code` | string | Yes | Must exist in `lecturers.csv`. |
| `slot_code` | string | Yes | Must exist in `time_slots.csv`. |
| `mandatory` | boolean | Yes | `true` means an officially confirmed hard restriction; `false` means ordinary soft preference data. Lecturer self-declared preferences should normally be `false`. |
| `reason` | string | No | Note only. Do not infer rules from this text. |

## 7. `room_unavailable_slots.csv`

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `room_code` | string | Yes | Must exist in `rooms.csv`. |
| `slot_code` | string | Yes | Must exist in `time_slots.csv`. |
| `reason` | string | No | Note only. |

## 8. `academic_calendar.csv`

The GA creates a base weekly timetable before student registration. Academic calendar data is used afterward to expand base assignments into dated teaching occurrences.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `date` | date | Yes | ISO date `YYYY-MM-DD`, unique in the dataset. |
| `academic_week` | integer | Yes | Academic week number. |
| `day_of_week` | integer | Yes | `2` to `8`, Monday to Sunday. |
| `is_teaching_day` | boolean | Yes | `true` means normal occurrences may be generated. |
| `is_holiday` | boolean | Yes | `true` means no normal occurrence should be generated for that date. |
| `holiday_name` | string | No | Holiday or non-teaching-day name. |
| `note` | string | No | Optional note. |

When a regular class date falls on a holiday or non-teaching day, the system must not generate a normal occurrence and must not automatically move it to another date.
