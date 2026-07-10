# CSV Validation Rules

This document turns SRS rules `DV-01` to `DV-12` into implementation-ready validation checks.

## 1. Validation Error Shape

Backend validation should return errors in this shape:

```json
{
  "file": "course_sections.csv",
  "row": 3,
  "column": "lecturer_code",
  "value": "GV999",
  "code": "DV-05",
  "message": "Lecturer code does not exist in lecturers.csv"
}
```

Use 1-based row numbers including the header row. For file-level errors, `row`, `column` and `value` may be `null`.

## 2. Rule Matrix

| Code | Rule | Implementation note |
| --- | --- | --- |
| DV-01 | File must be readable CSV. | Reject files that cannot be decoded as UTF-8 CSV. |
| DV-02 | Required columns must not be missing. | Compare headers against `docs/requirements/data-schema.md`. |
| DV-03 | Identifiers and required fields must not be blank. | Validate every required field after trimming whitespace. |
| DV-04 | Numeric values must have valid type and be greater than 0 where required. | Parse integers strictly; reject decimals and text values. |
| DV-05 | Lecturer and room references must exist. | Validate references after loading master files. |
| DV-06 | Course-section code must not duplicate within the same import batch. | Detect duplicates in `course_sections.csv`. |
| DV-07 | Course type and room type must be in allowed dictionaries. | MVP allowed values: `LY_THUYET`, `THUC_HANH`. |
| DV-08 | Time slots must be in the valid slot list. | Validate all slot references against active `time_slots.csv` rows. |
| DV-09 | System must report row, column, value and reason. | Use the validation error shape in this document. |
| DV-10 | User must confirm before overwriting an existing import batch. | Implement in backend/API flow before saving, not only frontend. |
| DV-11 | Room capacity must be greater than or equal to `scheduling_student_count`. | Check room suitability during scheduling and manual changes. |
| DV-12 | If real files use different column names, system must map to the standard model before saving. | MVP may reject unknown headers with a clear message; flexible mapping can be added later. |

## 3. File-Level Checks

- File extension should be `.csv`.
- File name must be treated as untrusted input.
- Empty files are invalid.
- Header row is required.
- Duplicate column names are invalid.
- Unexpected columns are allowed only if the importer explicitly supports ignoring them.

## 4. Cross-File Checks

- `course_sections.lecturer_code` must exist in `lecturers.lecturer_code`.
- `lecturer_unavailable_slots.lecturer_code` must exist in `lecturers.lecturer_code`.
- `lecturer_unavailable_slots.slot_code` must exist in `time_slots.slot_code`.
- `room_unavailable_slots.room_code` must exist in `rooms.room_code`.
- `room_unavailable_slots.slot_code` must exist in `time_slots.slot_code`.
- Time slots referenced by unavailable-slot files should be active unless the business rule later allows inactive references.

## 5. Warnings vs Errors

### Errors

Errors block saving an import batch or running GA.

- Missing required columns.
- Blank required identifiers.
- Invalid numeric values.
- Unknown references.
- Duplicate course-section codes.
- Invalid enum values.

### Warnings

Warnings may be shown without blocking, unless later confirmed as hard rules.

- Missing optional `campus_code`.
- Missing optional preferred slots.
- Empty notes.
- Soft workload preferences not provided.

