# CSV Validation Rules

This document turns the updated SRS data rules into implementation-ready validation checks.

## 1. Validation Error Shape

Backend validation should identify the file, row, column, invalid value and reason.

```json
{
  "file": "course_sections.csv",
  "row": 3,
  "column": "lecturer_code",
  "value": "GV999",
  "reason": "Mã giảng viên không tồn tại"
}
```

Use 1-based row numbers including the header row. For file-level errors, `row`, `column` and `value` may be `null` or empty depending on the response layer.

## 2. Rule Matrix

| Code | Rule | Implementation note |
| --- | --- | --- |
| DV-01 | File must be readable CSV. | Decode as UTF-8 or UTF-8 with BOM. Reject unreadable files. |
| DV-02 | Required columns must not be missing. | Compare headers against `docs/requirements/data-schema.md`. |
| DV-03 | Required identifiers and fields must not be blank. | Trim whitespace before validation. |
| DV-04 | Numeric values must have valid type and range. | Parse integers strictly; reject invalid or non-positive required numbers. |
| DV-05 | Cross-file references must exist. | Validate lecturer, room and slot references after loading master files. |
| DV-06 | Course-section code must not duplicate within an import batch. | Detect duplicate `section_code` values. |
| DV-07 | Enum values must be in allowed dictionaries. | Course types: `THEORY`, `PRACTICE`, `INTEGRATED`; room types: `THEORY_ROOM`, `COMPUTER_LAB`, `SPECIALIZED_LAB`. |
| DV-08 | Time slots must be configured valid slots. | Reject arbitrary period ranges. Validate slot ranges and `supports_course_types`. |
| DV-09 | System must report actionable validation errors. | Include file, row, column, value and reason. |
| DV-10 | User must confirm before saving or replacing an import batch. | Implement in backend/API flow before persistence. |
| DV-11 | Room suitability must be checkable. | Capacity and room type are hard constraints for scheduling. |
| DV-12 | Unknown real-world file formats need explicit mapping. | MVP may reject unknown schemas; flexible mapping can be added later. |
| DV-13 | A confirmed import batch used by a GA run must remain immutable. | A correction is saved as a new batch/version; do not overwrite data referenced by an existing run. |

## 3. File-Level Checks

- File extension should be `.csv`.
- Empty files are invalid.
- Header row is required.
- Duplicate column names are invalid.
- UTF-8 Vietnamese text must be preserved.
- Unexpected columns may be ignored only when the importer explicitly supports that behavior.

## 4. Cross-File Checks

- `course_sections.lecturer_code` must exist in `lecturers.lecturer_code`.
- `lecturer_time_preferences.lecturer_code` must exist in `lecturers.lecturer_code`.
- `lecturer_time_preferences.slot_code` must exist in `time_slots.slot_code`.
- `room_unavailable_slots.room_code` must exist in `rooms.room_code`.
- `room_unavailable_slots.slot_code` must exist in `time_slots.slot_code`.
- A course section must have at least one locally feasible time slot and room before GA starts.
- `academic_calendar.date` values must be valid ISO dates.
- Academic calendar `day_of_week` must be in the same `2` to `8` format used by time slots.

## 5. Blocking Errors

Errors block saving an import batch or running GA:

- Missing required files or columns.
- Blank required identifiers.
- Invalid numeric values.
- Unknown references.
- Duplicate course-section codes.
- Invalid enum values.
- No compatible time slot for a section.
- No compatible room for a section.
- `scheduling_student_count` not matching the priority rule.
- Invalid academic calendar date or day-of-week value.

## 6. Non-Blocking Notes

These may be shown as warnings or stored as notes:

- Empty optional `notes`.
- Missing optional preferences.
- Non-mandatory lecturer time-preference rows.
