# Backend AGENTS.md

## 1. Scope

This file provides instructions for AI coding agents modifying files under
`backend/`.

It extends the repository-wide `/AGENTS.md`.

Before modifying backend files, read:

1. `/AGENTS.md`
2. This file
3. The assigned GitHub Issue
4. Relevant requirement and design documents
5. Existing backend code and tests

For Genetic Algorithm files, also read:

```text
backend/app/algorithms/genetic/AGENTS.md
```

Repository-wide rules continue to apply unless this file provides a more
specific backend rule.

---

## 2. Backend purpose

The backend is responsible for:

- Authentication and authorization.
- CSV upload and validation.
- Import-batch management.
- Lecturer, room, course-section and time-slot data.
- Genetic Algorithm configuration and execution.
- Timetable persistence and retrieval.
- Conflict detection.
- Timetable adjustment requests.
- Approval and rejection workflows.
- CSV and Excel export.
- Run-history and experiment metrics.
- Backend API validation and error handling.

The backend must be the authoritative location for business rules.

Frontend validation may improve user experience, but it must not replace
backend validation.

---

## 3. Current project state

The backend may still be in the initialization stage.

Do not assume that the following already exist:

- A FastAPI application.
- A dependency-management file.
- SQLAlchemy models.
- Alembic migrations.
- A PostgreSQL connection.
- Authentication.
- A test suite.
- Ruff or another linter.
- Docker configuration.
- Background-task infrastructure.
- A finalized directory structure.

Inspect existing files before creating new ones.

Do not generate the entire planned backend architecture during a small task.

---

## 4. Expected technology

The intended backend stack is:

- Python.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- Alembic.
- PostgreSQL.
- pandas when appropriate for tabular import processing.
- openpyxl for Excel export when appropriate.
- pytest for automated testing.

These technologies are planned until the project configuration formally
adopts them.

Do not replace a primary technology without explicit approval.

Do not add a dependency before checking whether the standard library or an
existing dependency already solves the problem clearly.

---

## 5. Intended backend structure

The intended structure is similar to:

```text
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   └── routes/
│   ├── algorithms/
│   │   └── genetic/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── migrations/
├── tests/
├── AGENTS.md
└── pyproject.toml
```

This is a direction, not a requirement to create every directory immediately.

Create a directory only when the current Issue requires it.

Avoid placeholder files and empty abstractions without a current use.

---

## 6. Layer responsibilities

### 6.1. API routes

API routes should:

- Receive and validate HTTP input.
- Resolve authentication and authorization dependencies.
- Call an application service.
- Translate service results into HTTP responses.
- Return appropriate status codes.
- Avoid exposing internal exceptions.

API routes should not:

- Contain the Genetic Algorithm implementation.
- Contain long database queries.
- Repeat business rules.
- Commit database transactions in several unrelated places.
- Return raw database models without an intentional response schema.

Keep route handlers thin.

### 6.2. Schemas

Pydantic schemas should represent:

- Requests.
- Responses.
- Query parameters.
- Import-validation errors.
- Genetic Algorithm configuration.
- Timetable results.
- Adjustment requests.
- Pagination metadata when needed.

Use separate request and response schemas when their responsibilities differ.

Do not expose:

- Password hashes.
- Internal secrets.
- Sensitive audit information.
- Database-only fields that clients do not need.

### 6.3. Services

Services should contain application and business logic, including:

- Import workflows.
- Validation coordination.
- Timetable generation workflows.
- Conflict checking.
- Approval workflows.
- Export coordination.
- Transaction boundaries when appropriate.

A service may coordinate repositories and domain logic.

A service should not depend on React components or browser behavior.

### 6.4. Repositories

Repositories should be responsible for data access, such as:

- Reading entities.
- Persisting entities.
- Filtering and pagination.
- Query composition.
- Database-specific operations.

Repositories should not contain:

- Fitness calculations.
- Scheduling constraints.
- Authorization policy decisions.
- Approval-workflow decisions.
- HTTP response construction.

### 6.5. Domain and constraint logic

Reusable domain rules should be independent of HTTP.

The same conflict-checking logic should be reusable by:

- Automatic timetable generation.
- Manual timetable changes.
- Adjustment-request approval.
- Tests.
- Final timetable validation.

Do not create separate, inconsistent implementations for the same rule.

---

## 7. Python conventions

Use English for:

- Module names.
- Class names.
- Function names.
- Variables.
- Enums.
- Database identifiers.
- API field names unless an external contract requires otherwise.

User-facing messages may be Vietnamese.

### 7.1. Naming

Use:

```python
lecturer_code
course_section
validate_time_conflict
TimetableRunService
RoomRepository
```

Avoid:

```python
maGV
ktraPhong
data1
tmp2
xu_ly
```

### 7.2. Type hints

Use type hints for:

- Public functions.
- Service methods.
- Repository methods.
- Domain objects.
- Algorithm interfaces.
- Non-obvious local structures.

Do not add meaningless type annotations that make code harder to understand.

### 7.3. Functions

Prefer functions that:

- Have one clear responsibility.
- Use descriptive names.
- Have limited side effects.
- Return structured results.
- Are independently testable.

Avoid very large functions that combine:

- Parsing.
- Validation.
- Database writes.
- Business rules.
- Response formatting.

### 7.4. Exceptions

Use specific exceptions.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Do not silently ignore failures.

Expected domain errors should be represented deliberately, for example:

- Entity not found.
- Duplicate identifier.
- Invalid import data.
- Permission denied.
- Timetable conflict.
- Invalid state transition.

Unexpected errors should be logged safely and converted to a generic client
response.

### 7.5. Mutable defaults

Do not use mutable default arguments.

Avoid:

```python
def validate(errors=[]):
    ...
```

Use:

```python
def validate(errors: list[str] | None = None):
    current_errors = [] if errors is None else errors
```

---

## 8. FastAPI rules

### 8.1. Application construction

Prefer an application factory or clearly structured application initialization
when it improves testing and configuration.

Do not put all routes and setup code into one large `main.py`.

### 8.2. Dependency injection

Use FastAPI dependencies for concerns such as:

- Database sessions.
- Current authenticated user.
- Permission checking.
- Configuration access.
- Shared request-level dependencies.

Do not hide major business operations inside a dependency.

### 8.3. Status codes

Choose status codes based on behavior.

Typical examples:

- `200 OK` for successful reads or updates.
- `201 Created` for created resources.
- `204 No Content` for successful operations with no response body.
- `400 Bad Request` for malformed workflows not covered by schema validation.
- `401 Unauthorized` when authentication is missing or invalid.
- `403 Forbidden` when the user lacks permission.
- `404 Not Found` when a requested resource does not exist.
- `409 Conflict` for duplicate or conflicting state.
- `422 Unprocessable Entity` for structured validation failures.

Follow the established project convention once one exists.

Do not return `200 OK` for every outcome.

### 8.4. API response consistency

Use consistent response formats.

A structured validation error may resemble:

```json
{
  "code": "CSV_VALIDATION_FAILED",
  "message": "Dữ liệu nhập không hợp lệ.",
  "details": [
    {
      "row": 12,
      "column": "lecturer_code",
      "value": "GV999",
      "code": "LECTURER_NOT_FOUND",
      "message": "Mã giảng viên không tồn tại."
    }
  ]
}
```

Do not return raw Python exception messages to clients.

---

## 9. Authentication and authorization

Authentication and authorization rules must be enforced by the backend.

Expected roles may include:

- Training Department staff or timetable manager.
- Lecturer.
- Technical administrator.

Do not trust:

- A role sent by the frontend.
- A lecturer identifier sent by the client without ownership verification.
- Hidden frontend controls as sufficient authorization.

### 9.1. Lecturer restrictions

A lecturer must not be allowed to:

- View unauthorized lecturer data.
- Modify another lecturer’s timetable.
- Submit requests for unrelated course sections.
- Add or delete assigned course sections.
- Approve their own timetable changes unless explicitly authorized.
- Access Training Department management functions.

### 9.2. Credentials

Never:

- Store plain-text passwords.
- Return password hashes.
- Log complete tokens.
- Put authentication secrets in source code.
- Store backend secrets in frontend configuration.

Authentication implementation must be covered by tests for both allowed and
forbidden access.

---

## 10. Database and SQLAlchemy

### 10.1. Model responsibilities

Database models represent persistence.

Do not place large workflow logic directly inside ORM models.

Simple domain invariants may be represented close to the model when this keeps
the code clear, but application workflows belong in services.

### 10.2. Constraints

Use database constraints where appropriate:

- Primary keys.
- Foreign keys.
- Unique identifiers.
- Required columns.
- Simple check constraints.
- Unique combinations.

Application validation is still required for clear user-facing errors and
complex rules.

### 10.3. Transactions

Use a transaction for operations that must succeed or fail together.

Examples:

- Creating an import batch and its imported rows.
- Saving a Genetic Algorithm run and its generated timetable.
- Approving an adjustment request and updating the timetable.
- Applying several related schedule changes.
- Updating status and audit information together.

Do not leave partially updated business state after an exception.

### 10.4. Query behavior

Avoid:

- Database queries inside large loops.
- Loading complete tables when only a subset is needed.
- N+1 query patterns.
- Returning unbounded result sets.
- Duplicate queries for the same request without reason.

Do not introduce complex optimization before measuring actual behavior.

### 10.5. Sessions

Database session lifecycle should be explicit and consistent.

Do not create uncontrolled global sessions.

Do not keep transactions open while executing long-running Genetic Algorithm
work unless there is a specific documented reason.

---

## 11. Alembic migrations

When Alembic is configured:

- Every schema change must have a migration.
- Review generated migrations before committing.
- Use descriptive migration messages.
- Do not ask team members to edit shared databases manually.
- Do not modify a migration that has already been used by other members.
- Create a new migration for later corrections.
- Document destructive changes.

A Pull Request with a migration must state:

- What schema changed.
- How to apply the migration.
- Whether existing data is affected.
- Whether rollback is safe.

Do not delete a table or column without explicit approval.

---

## 12. CSV import

### 12.1. Input safety

Treat uploaded files as untrusted input.

Validate:

- File type.
- File size.
- Encoding.
- Required headers.
- Duplicate headers.
- Empty files.
- Row count when relevant.
- Required values.
- Numeric values.
- Enum values.
- Referential identifiers.
- Duplicate business identifiers.

Do not trust only the file extension or client-provided MIME type.

### 12.2. Parsing and validation separation

Prefer separate stages:

```text
Receive file
    ↓
Read and parse
    ↓
Normalize headers and values
    ↓
Validate structure
    ↓
Validate each row
    ↓
Validate cross-file references
    ↓
Produce preview and error report
    ↓
User confirmation
    ↓
Persist import batch
```

Do not persist invalid rows silently unless the documented requirement
explicitly permits partial import.

### 12.3. Validation errors

Errors should include enough information for correction:

- Row number.
- Column name.
- Original value.
- Machine-readable code.
- Human-readable message.

Keep original row numbering understandable to users, accounting for the CSV
header.

### 12.4. Large files

Do not load arbitrarily large files without controls.

When actual data size is known, choose an appropriate strategy:

- Full in-memory parsing for verified small files.
- Chunked parsing for larger files.
- Background processing when runtime justifies it.

Do not add background infrastructure before it is required.

---

## 13. Timetable and conflict validation

Conflict checking must be centralized and reusable.

At minimum, relevant operations should check:

- Lecturer time conflicts.
- Room time conflicts.
- Course-section session requirements.
- Room-type compatibility.
- Room-capacity rules after they are confirmed.
- Lecturer unavailable slots.
- Room unavailable slots.
- Active time slots.
- Valid entity references.

Manual changes must use the same authoritative rules as automatic scheduling.

A successful API response must not be returned before required checks pass.

Return all useful detected conflicts where feasible instead of stopping after
the first error, unless the operation must fail immediately.

---

## 14. Adjustment requests

Expected request types may include:

- Suspend one session.
- Move one session.
- Change room.
- Move an entire recurring schedule when allowed.

Do not finalize uncertain workflow rules without confirmation.

State transitions should be explicit, such as:

```text
PENDING
APPROVED
REJECTED
CANCELLED
APPLIED
```

The exact states must follow the SRS when finalized.

Invalid transitions must be rejected.

When applicable, preserve audit information:

- Requester.
- Reviewer.
- Created time.
- Reviewed time.
- Reason.
- Rejection note.
- Previous schedule.
- Proposed schedule.
- Applied result.

Approval and schedule application should be transactionally consistent.

---

## 15. Genetic Algorithm integration

The backend service may coordinate Genetic Algorithm execution, but the
algorithm implementation must remain isolated from HTTP concerns.

The backend may be responsible for:

- Loading normalized scheduling input.
- Validating configuration.
- Starting a run.
- Recording run status.
- Invoking the algorithm.
- Persisting the result.
- Exposing metrics.
- Handling cancellation if later required.

The backend route or service must not reimplement:

- Chromosome logic.
- Fitness rules.
- Genetic operators.
- Constraint evaluation.

Read the local algorithm instructions before modifying those components:

```text
backend/app/algorithms/genetic/AGENTS.md
```

Long-running execution must not hold unnecessary database transactions.

Do not add a task queue until runtime requirements demonstrate that it is
needed and the team approves it.

---

## 16. Export rules

CSV and Excel exports must:

- Represent the selected or effective timetable.
- Preserve Vietnamese text correctly.
- Use stable and documented column names.
- Avoid exposing internal identifiers that users do not need.
- Handle empty results.
- Use appropriate content types and filenames.
- Be tested against representative data.

Export formatting should be separated from database queries and route logic.

Do not make the exported file disagree with the timetable displayed by the
system.

---

## 17. Logging

Use structured, useful logging where configured.

Log events such as:

- Import started or completed.
- Import validation failed.
- Genetic Algorithm run started or completed.
- Adjustment request changed state.
- Unexpected backend failure.

Do not log:

- Passwords.
- Password hashes.
- Full authentication tokens.
- Secret keys.
- Entire uploaded files.
- Sensitive personal information without necessity.

Include identifiers useful for tracing, such as:

- Request ID.
- Import-batch ID.
- Algorithm-run ID.
- Adjustment-request ID.

Do not use `print()` as permanent application logging.

---

## 18. Backend testing

Use pytest once configured.

Tests should be deterministic and isolated.

### 18.1. Unit tests

Use unit tests for:

- Pure validation functions.
- Service rules.
- State transitions.
- Conflict checking.
- Export transformations.
- Authorization-policy helpers.
- Algorithm-independent domain logic.

### 18.2. API tests

Use API tests for:

- Request validation.
- Response schemas.
- HTTP status codes.
- Authentication.
- Authorization.
- Error responses.
- Transactional workflows.

### 18.3. Database tests

Database tests must:

- Use an isolated test database or supported test strategy.
- Clean up state between tests.
- Avoid production credentials.
- Avoid dependence on test execution order.
- Verify transaction rollback where relevant.

### 18.4. Import tests

Include cases such as:

- Valid CSV.
- Empty CSV.
- Missing required column.
- Duplicate column.
- Invalid encoding.
- Missing required value.
- Invalid numeric value.
- Unknown lecturer.
- Duplicate course-section code.
- Invalid room type.
- Multiple errors in one file.

### 18.5. Authorization tests

For protected endpoints, test:

- Anonymous access.
- Correct role.
- Incorrect role.
- Access to owned records.
- Access to another user’s records.

Do not only test successful requests.

---

## 19. Backend commands

Check the actual project configuration before running commands.

When the relevant tools are configured, expected commands may include:

```bash
cd backend
pytest
```

```bash
cd backend
ruff check .
```

```bash
cd backend
ruff format --check .
```

```bash
cd backend
alembic upgrade head
```

Do not report these commands as successful unless they were actually run.

If `pyproject.toml`, pytest, Ruff or Alembic is not yet configured, report that
fact instead of pretending the check exists.

---

## 20. Backend Definition of Done

A backend task is complete when applicable conditions are satisfied:

- API behavior matches the Issue and requirements.
- Request and response schemas are defined.
- Authorization is enforced at the backend.
- Business logic is not duplicated in routes.
- Database changes have reviewed migrations.
- Transactions protect multi-step updates.
- Input and error cases are handled.
- Relevant tests are added.
- Tests and configured checks pass.
- No secret or local configuration is committed.
- Documentation is updated when contracts change.
- Remaining assumptions are reported.

Do not declare completion based only on a successful manual request.

---

## 21. Final report for backend changes

After modifying backend files, report:

### Summary

What behavior changed.

### Files

List created, modified and deleted files.

### API impact

State:

- Endpoints added or changed.
- Request or response schema changes.
- Status-code changes.
- Authorization changes.

### Database impact

State:

- Models changed.
- Migration added.
- Existing data impact.

### Verification

List commands run and results.

### Assumptions and risks

List unresolved requirements and unverified behavior.
