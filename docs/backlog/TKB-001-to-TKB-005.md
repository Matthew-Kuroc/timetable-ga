# Initial Backlog: TKB-001 to TKB-005

This backlog defines the first five tasks that must be completed before backend, frontend and GA work proceed in parallel.

## TKB-001: Normalize UR/SRS Documents Into Repository

### Goal

Create repository-readable requirement documents from the provided Word files.

### Requirement Sources

- `D:\DoAn\DuAn\TaiLieu_UR.docx`
- `D:\DoAn\DuAn\TaiLieu_SRS.docx`
- `docs/requirements/UR.md`
- `docs/requirements/SRS.md`

### Scope

- Create Markdown requirement documents in `docs/requirements`.
- Keep requirement IDs, data rules, constraints and acceptance criteria traceable.
- Mark draft or unconfirmed business rules clearly.

### Acceptance Criteria

- `docs/requirements/UR.md` exists.
- `docs/requirements/SRS.md` exists.
- Functional requirement IDs such as `FR-DATA`, `FR-GA`, `FR-VIEW`, `FR-REQ`, `FR-EXP` are preserved.
- Constraint IDs such as `HC-*`, `SC-*` and validation IDs such as `DV-*` are preserved.

### Owner

Phi, with review by the whole group.

## TKB-002: Define CSV Schema and Small Sample Dataset

### Goal

Define the minimum CSV structures needed for the MVP and provide a small dataset that can be used by backend validation, GA prototype and frontend mock screens.

### Scope

- Define CSV files for:
  - lecturers
  - rooms
  - time slots
  - course sections
  - lecturer unavailable slots
  - room unavailable slots
- Provide a small valid sample dataset.
- Use fake/non-personal sample data.

### Acceptance Criteria

- `docs/requirements/data-schema.md` documents all MVP CSV fields.
- Sample files exist under `data/samples/small`.
- Sample data is consistent enough to run a first GA prototype.
- No real personal data is included.

### Owner

Phi and Huy, with frontend review by Tien.

## TKB-003: Define CSV Validation Rules

### Goal

Translate SRS validation rules `DV-01` to `DV-12` into implementation-ready checks.

### Scope

- Document required columns.
- Document type checks.
- Document reference checks.
- Document duplicate checks.
- Document capacity checks.
- Define expected validation-error shape.

### Acceptance Criteria

- `docs/requirements/validation-rules.md` exists.
- Every `DV-*` rule from SRS has an implementation note.
- Validation error output includes file, row, column, value, code and message.

### Owner

Phi.

## TKB-004: Define Hard Constraints for GA and Manual Changes

### Goal

Turn SRS hard constraints `HC-01` to `HC-12` into a shared contract for GA, backend conflict checking and request approval.

### Scope

- Document each hard constraint.
- Define what data is needed to check it.
- Define where it applies: GA generation, import validation, manual change or approval workflow.

### Acceptance Criteria

- `docs/requirements/scheduling-constraints.md` exists.
- Every `HC-*` rule from SRS has an implementation note.
- Room-capacity checking uses `scheduling_student_count` as the current draft rule.
- Unconfirmed rules are marked as open issues rather than silently assumed.

### Owner

Huy, with backend integration review by Phi.

## TKB-005: Define Timetable Output Contract

### Goal

Define the standard output shape produced by GA and consumed by backend APIs, frontend timetable views and export logic.

### Scope

- Define timetable session fields.
- Define run metrics fields.
- Define violation report fields.
- Provide a sample output CSV.

### Acceptance Criteria

- `docs/requirements/timetable-output.md` exists.
- `data/samples/small/expected_timetable.csv` exists.
- Output supports timetable views by lecturer, room and course section.
- Output includes enough fields for CSV/Excel export.

### Owner

Phi and Huy, with frontend review by Tien.

## Recommended Execution Order

1. Finish `TKB-001`, `TKB-002`, `TKB-003`, `TKB-004`, `TKB-005`.
2. Huy starts GA prototype using `data/samples/small`.
3. Phi starts backend skeleton and CSV validation.
4. Tien starts frontend mock screens using the same sample data and output contract.
5. Integrate GA into backend only after `expected_timetable.csv` shape is agreed.

