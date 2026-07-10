# Frontend AGENTS.md

## 1. Scope

This file defines instructions for AI coding agents modifying files under:

```text
frontend/
```

It extends the repository-wide:

```text
/AGENTS.md
```

All repository-wide rules remain active.

Before modifying frontend files, read:

1. `/AGENTS.md`
2. This file
3. The assigned GitHub Issue
4. Relevant URS and SRS sections
5. Relevant API and UI documents
6. Existing frontend code and tests

Do not assume that every planned screen or component has already been
implemented.

---

## 2. Frontend responsibility

The frontend provides the web user interface for the timetable scheduling
system.

It may be responsible for:

- User authentication screens.
- Role-aware navigation.
- CSV upload interfaces.
- Import preview and validation-error display.
- Genetic Algorithm configuration forms.
- Run-status and progress displays.
- Timetable views by lecturer, room and course section.
- Lecturer weekly timetable views.
- Timetable adjustment-request forms.
- Approval and rejection interfaces for authorized users.
- Run-history and experiment-result screens.
- CSV and Excel export actions.
- Clear loading, empty, success and error states.

The frontend is not the authoritative location for business rules.

The backend must remain responsible for:

- Authentication validation.
- Authorization.
- Data validation.
- Conflict detection.
- Hard-constraint enforcement.
- Timetable validity.
- Approval workflow enforcement.
- Final export data.

Frontend validation may improve user experience, but it must not replace
backend validation.

---

## 3. Current project state

The frontend may still be in the initialization stage.

Do not assume that the following already exist:

- A React application.
- TypeScript configuration.
- Vite configuration.
- Material UI.
- Routing.
- API client.
- Authentication state.
- Test tooling.
- Lint configuration.
- Formatting configuration.
- Environment variables.
- A finalized folder structure.
- Reusable timetable components.

Inspect existing files before creating new ones.

Do not generate the complete planned frontend for a small Issue.

Create only the files required for the current task.

---

## 4. Expected technology

The intended frontend stack is:

- React.
- TypeScript.
- Vite.
- Material UI.
- A centralized HTTP client.
- Appropriate React testing tools.
- ESLint or equivalent lint tooling.
- A formatter when formally configured.

These technologies remain planned until the repository formally configures
them.

Do not replace React, TypeScript, Vite or Material UI without explicit
approval.

Do not introduce a large state-management, form, table or calendar library
before demonstrating that the current project needs it.

Before adding a dependency, explain:

- What problem it solves.
- Why existing tools are insufficient.
- Its maintenance status.
- Its bundle-size impact.
- Its security implications.
- Whether a simpler implementation is possible.

---

## 5. Intended frontend structure

The intended structure may resemble:

```text
frontend/
├── public/
├── src/
│   ├── app/
│   ├── assets/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── imports/
│   │   ├── algorithm/
│   │   ├── timetables/
│   │   ├── adjustments/
│   │   └── run-history/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── types/
│   ├── utils/
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/
├── AGENTS.md
├── package.json
├── tsconfig.json
└── vite.config.ts
```

This is a direction, not a requirement to create all directories
immediately.

Create a directory only when the current Issue requires it.

Avoid:

- Empty feature folders.
- Placeholder components with no use.
- Generic abstractions created only for possible future requirements.
- A single `components/` directory containing the entire application without
  feature organization.

---

## 6. Component responsibilities

### 6.1. Pages

Pages should:

- Represent route-level screens.
- Coordinate feature components.
- Read route parameters.
- Trigger page-level data loading.
- Display page-level loading and error states.
- Avoid containing large reusable UI implementations.

Pages should not contain:

- Complete API client implementations.
- Database knowledge.
- Scheduling algorithms.
- Large repeated form logic.
- Hard-coded permission decisions.

### 6.2. Feature components

Feature components should represent domain-specific interface sections.

Examples:

```text
CsvUploadPanel
ImportPreviewTable
AlgorithmConfigurationForm
TimetableWeekView
RoomTimetableView
LecturerScheduleCard
AdjustmentRequestForm
RunMetricsPanel
ConflictList
```

Each component should have one clear responsibility.

### 6.3. Shared components

Shared components should be genuinely reusable.

Examples:

```text
LoadingState
EmptyState
ErrorAlert
ConfirmationDialog
PageHeader
StatusChip
FormFieldError
DataTable
```

Do not move a component into a shared directory after only one use unless its
responsibility is clearly generic.

### 6.4. Layouts

Layouts may contain:

- Application navigation.
- Header.
- Sidebar.
- Role-aware menu items.
- Main content area.
- Shared responsive behavior.

Layouts must not contain domain business logic.

---

## 7. TypeScript rules

Use TypeScript deliberately.

Do not use `any` when the type can reasonably be known.

Avoid:

```typescript
const data: any = response.data;
```

Prefer:

```typescript
const data: TimetableRunResponse = response.data;
```

### 7.1. Required domain types

Define explicit types when relevant for:

- User.
- Role.
- Lecturer.
- Room.
- Course section.
- Time slot.
- Timetable entry.
- Import batch.
- Import preview.
- Validation error.
- Genetic Algorithm configuration.
- Genetic Algorithm run.
- Fitness metrics.
- Adjustment request.
- Approval result.
- API error.
- Pagination metadata.

### 7.2. Request and response types

Do not assume a request type and response type are identical.

Example:

```typescript
interface CreateAdjustmentRequest {
  timetableEntryId: string;
  requestType: AdjustmentRequestType;
  proposedSlotCode?: string;
  proposedRoomCode?: string;
  reason: string;
}

interface AdjustmentRequestResponse {
  id: string;
  status: AdjustmentRequestStatus;
  createdAt: string;
  reviewedAt: string | null;
}
```

### 7.3. Union types and enums

Use union types or enums for stable controlled values.

Example:

```typescript
type AdjustmentRequestStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "CANCELLED"
  | "APPLIED";
```

Do not compare status values using unexplained strings scattered across
components.

### 7.4. Null and optional values

Handle nullable values explicitly.

Do not assume:

- Every API field is always present.
- Every timetable has results.
- Every request has been reviewed.
- Every room has a campus value.
- Every validation error has a row value.

Avoid non-null assertions unless the invariant is proven.

---

## 8. Naming conventions

Use English for code identifiers.

Use:

```text
TimetableWeekView
AdjustmentRequestForm
useCurrentUser
fetchLecturerTimetable
validationErrors
selectedRoomCode
```

Avoid:

```text
LichGV
formDoiLich
data1
tmp
xuLyLoi
```

User-facing text may be Vietnamese.

Use consistent naming:

- Components: `PascalCase`.
- Hooks: `useSomething`.
- Variables and functions: `camelCase`.
- Constants: follow the established project convention.
- Type names: `PascalCase`.
- File names: follow one consistent project convention.

Do not mix multiple naming conventions within the same feature.

---

## 9. React component rules

### 9.1. One clear responsibility

A component should focus on one responsibility.

Do not create a page component that simultaneously:

- Fetches all application data.
- Handles authentication.
- Validates CSV.
- Renders the timetable.
- Manages modal state.
- Exports Excel.
- Calculates business rules.

Split responsibilities when the component becomes difficult to understand or
test.

### 9.2. Props

Use explicit props.

Prefer:

```typescript
interface TimetableEntryCardProps {
  entry: TimetableEntry;
  canRequestAdjustment: boolean;
  onRequestAdjustment: (entryId: string) => void;
}
```

Avoid generic props such as:

```typescript
interface Props {
  data: any;
  config: any;
}
```

### 9.3. Derived state

Do not store values in state when they can be derived safely from existing
state or props.

Avoid duplicated sources of truth.

For example, do not store both:

```text
selectedRoom
selectedRoomCode
```

unless both are independently required and synchronized deliberately.

### 9.4. Effects

Use effects for external synchronization, not for ordinary value
calculation.

An effect must have:

- A clear purpose.
- Correct dependencies.
- Cleanup when required.
- Protection against stale asynchronous results when relevant.

Do not use effects to manually reproduce ordinary rendering behavior.

### 9.5. Keys

Use stable identifiers as React keys.

Prefer:

```tsx
{
  entries.map((entry) => <TimetableEntryCard key={entry.id} entry={entry} />);
}
```

Avoid using array indexes when list order or identity may change.

### 9.6. Conditional rendering

Make permission and state conditions understandable.

Avoid deeply nested ternary expressions.

Prefer named conditions or separate components.

---

## 10. Hooks

Custom hooks should package reusable stateful behavior.

Possible hooks:

```text
useCurrentUser
usePermissions
useImportPreview
useTimetableFilters
useAlgorithmRun
useAdjustmentRequests
```

A hook should not hide large, unrelated workflows.

Do not create a custom hook merely to wrap a single `useState` without adding
meaningful behavior.

Hooks that call APIs must expose relevant states, such as:

```typescript
{
  (data, isLoading, error, refetch);
}
```

The exact shape should follow the selected data-fetching approach.

---

## 11. API client rules

All HTTP calls should go through a centralized service or API client.

Do not scatter code such as:

```typescript
fetch("http://localhost:8000/api/...");
```

across components.

A preferred structure may include:

```text
src/services/apiClient.ts
src/features/imports/importApi.ts
src/features/timetables/timetableApi.ts
src/features/adjustments/adjustmentApi.ts
```

### 11.1. Base URL

The API base URL must come from environment configuration.

Example:

```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
```

Do not hard-code machine-specific addresses in feature components.

### 11.2. Authentication

Token or session handling must be centralized.

Do not:

- Append authentication headers manually in many files.
- Log complete tokens.
- Put backend secrets in frontend environment variables.
- Treat `VITE_` variables as private secrets.

Any value embedded in the frontend bundle can potentially be viewed by the
client.

### 11.3. Error conversion

Convert backend errors into a consistent frontend error model.

Example:

```typescript
interface ApiError {
  code: string;
  message: string;
  details?: ApiErrorDetail[];
  status?: number;
}
```

Do not force every component to understand raw HTTP-library exceptions.

### 11.4. Request cancellation

For requests that may become obsolete, consider cancellation or stale-result
protection.

Examples:

- Timetable filtering.
- Search input.
- Switching between runs.
- Leaving a page while data is loading.

Do not update unmounted or outdated views with stale request results.

---

## 12. Authentication and authorization UI

The frontend may:

- Show role-appropriate navigation.
- Hide unauthorized actions.
- Disable actions that are not currently permitted.
- Redirect unauthenticated users.
- Display an access-denied page.

The frontend must not be treated as the final authorization layer.

The backend must verify every protected action.

### 12.1. Role handling

Role values should be centralized.

Do not scatter string comparisons such as:

```typescript
user.role === "admin";
```

throughout the application.

Use a permission helper or established authorization utility.

Example:

```typescript
canApproveAdjustment(currentUser);
```

### 12.2. Unauthorized responses

Handle:

- `401 Unauthorized`.
- `403 Forbidden`.

Expected behavior may include:

- Clearing invalid local authentication state.
- Redirecting to login.
- Displaying access denied.
- Preserving a safe return location when appropriate.

Do not create infinite redirect loops.

---

## 13. Forms

Forms may include:

- Login.
- CSV upload.
- Algorithm configuration.
- Adjustment request.
- Approval or rejection.
- Timetable filtering.

### 13.1. Validation

Frontend validation should cover immediate user feedback, such as:

- Required fields.
- Number ranges.
- File presence.
- Supported extension.
- Text length.
- Percentage limits.
- Missing reason.

The backend remains authoritative.

Do not duplicate complex scheduling rules inside frontend forms.

### 13.2. Submission states

Every form submission should consider:

- Idle.
- Submitting.
- Success.
- Validation failure.
- Server failure.
- Unauthorized response.

Disable duplicate submission while a request is pending when appropriate.

Do not leave the user unsure whether the request was submitted.

### 13.3. Server-side field errors

Map backend validation details to relevant fields or rows when possible.

For CSV errors, display:

- Row.
- Column.
- Value.
- Error code or message.

Do not collapse a detailed backend validation report into one generic toast.

---

## 14. CSV upload interface

The CSV upload screen should support relevant states:

- No file selected.
- File selected.
- Uploading.
- Parsing.
- Preview available.
- Validation errors.
- Ready for confirmation.
- Import completed.
- Import failed.

### 14.1. File handling

The frontend may validate:

- File extension.
- File size.
- Whether a file was selected.

It must not claim that the content is valid until the backend validates it.

### 14.2. Preview

The preview should:

- Display headers.
- Display representative rows.
- Support long content safely.
- Clearly mark invalid cells or rows when data is available.
- Avoid rendering an unbounded number of rows at once.

### 14.3. Error report

Validation errors should be understandable and navigable.

Consider:

- Filtering by error type.
- Highlighting row and column.
- Showing the original value.
- Downloading an error report if the backend supports it.

Do not hide errors merely to simplify the table.

---

## 15. Genetic Algorithm configuration UI

Configuration fields may include:

- Population size.
- Number of generations.
- Mutation rate.
- Crossover rate.
- Selection method.
- Elitism.
- Random seed.
- Stopping criteria.
- Soft-constraint weights.

### 15.1. Numeric validation

Validate numeric fields clearly.

Examples:

- Population size must be positive.
- Generation count must be positive.
- Rates must be between `0` and `1`.
- Elitism must not exceed population limits.
- Weights must not be negative unless explicitly allowed.

Do not silently clamp invalid values unless the product requirement specifies
that behavior.

### 15.2. Advanced settings

Do not overwhelm users with every experimental parameter on the default
screen.

When appropriate, separate:

- Basic settings.
- Advanced settings.

Display useful descriptions for technical terms.

### 15.3. Run submission

Before starting a run, show:

- Selected data batch.
- Main parameter values.
- Confirmation when the run may take significant time.

Prevent accidental duplicate run requests.

---

## 16. Algorithm run status

The run-status UI may display:

- Queued.
- Running.
- Completed.
- Failed.
- Cancelled if supported.
- Progress information when available.
- Current generation when available.
- Best fitness.
- Hard-violation count.
- Execution time.

Do not invent progress percentages when the backend does not provide reliable
progress information.

If only run status is available, display status honestly.

Polling must:

- Use a reasonable interval.
- Stop when the run reaches a terminal state.
- Stop when the component unmounts.
- Handle temporary errors.
- Avoid creating multiple simultaneous polling loops.

Do not add WebSocket infrastructure unless the project explicitly adopts it.

---

## 17. Timetable views

The system should support timetable views by:

- Lecturer.
- Room.
- Course section.

Lecturers should be able to view their own timetable by week.

### 17.1. Timetable entry display

A timetable entry may display:

- Course name.
- Course code.
- Section code.
- Lecturer.
- Room.
- Day.
- Start period.
- End period.
- Week.
- Status.

Do not rely on color alone to communicate status.

### 17.2. Weekly view

A weekly timetable should clearly represent:

- Monday through Sunday when required.
- Morning, afternoon and evening periods.
- Empty time slots.
- Overlapping or invalid states when the backend reports them.
- Current or selected week.
- Entry details.

Do not assume every session is exactly the same duration unless the confirmed
requirements guarantee it.

### 17.3. Filters

Filters may include:

- Lecturer.
- Room.
- Course section.
- Week.
- Day.
- Session type.
- Status.

Filter state should be predictable.

When filter state is stored in the URL, use clear query parameter names.

Do not send a request on every keystroke without debouncing when search traffic
could become excessive.

### 17.4. Large timetables

For large datasets, consider:

- Pagination.
- Virtualization.
- Server-side filtering.
- Collapsible groups.
- Limited default ranges.

Do not introduce complex optimization until a real rendering problem is
measured.

---

## 18. Timetable adjustments

Adjustment actions may include:

- Suspend one session.
- Move one session.
- Change room.
- Move an entire recurring schedule when allowed.

The frontend must clearly distinguish:

- Requested change.
- Approved change.
- Rejected change.
- Applied change.
- Current effective timetable.

### 18.1. Request form

The form should display:

- Current timetable entry.
- Request type.
- Reason.
- Proposed time slot when relevant.
- Proposed room when relevant.
- Confirmation before submission.

Do not allow a lecturer to select unrelated course sections through frontend
state.

The backend must still verify ownership.

### 18.2. Conflict responses

When the backend rejects a change because of conflicts, show useful details.

Examples:

- Lecturer conflict.
- Room conflict.
- Invalid room type.
- Room capacity violation.
- Lecturer unavailable.
- Room unavailable.
- Invalid slot.

Do not show only:

```text
Không thể thay đổi lịch.
```

when structured details are available.

### 18.3. Approval screen

Authorized users should be able to:

- View the request.
- Compare the current and proposed schedule.
- View conflict-check results.
- Approve.
- Reject with a reason.
- See processing state.

Destructive or irreversible actions should require confirmation.

---

## 19. Loading, empty, error and success states

Every data-driven page must consider four minimum states:

1. Loading.
2. Error.
3. Empty.
4. Success.

### 19.1. Loading

Use an appropriate loading indicator.

Do not show stale content as current without indicating refresh behavior.

Avoid blocking the entire application for a small local request.

### 19.2. Empty

Empty state text should explain:

- Why there may be no data.
- What the user can do next.
- Whether filters are active.

Examples:

```text
Chưa có lần chạy thuật toán nào.
```

```text
Không tìm thấy lịch phù hợp với bộ lọc hiện tại.
```

### 19.3. Error

Show actionable messages where possible.

Differentiate:

- Network error.
- Validation error.
- Unauthorized.
- Forbidden.
- Not found.
- Conflict.
- Unexpected server error.

Provide retry actions when safe.

### 19.4. Success

Use success messages for completed user actions, such as:

- Import confirmed.
- Adjustment request submitted.
- Request approved.
- File export started.

Do not show repeated success toasts for background refreshes.

---

## 20. User feedback and notifications

Use a consistent notification approach.

Notifications should:

- Be concise.
- Explain the result.
- Avoid exposing internal error details.
- Avoid disappearing before the user can understand critical failures.
- Not be the only place where field-level validation is shown.

Use inline errors for form fields and detailed validation tables.

Use notifications for overall operation outcomes.

---

## 21. Styling and Material UI

When Material UI is adopted:

- Use the theme rather than scattering arbitrary values.
- Use consistent spacing.
- Use semantic variants.
- Avoid deeply nested inline style objects.
- Reuse common visual patterns.
- Keep responsive behavior intentional.

Do not create a custom design system before the project needs one.

Avoid hard-coded colors for domain meaning without theme support.

Status colors should be accompanied by text or icons.

### 21.1. Responsive behavior

Primary screens should remain usable on common laptop and desktop widths.

Mobile optimization is not the main scope, but the interface should avoid
unnecessary breakage on narrower screens.

Tables may use:

- Horizontal scrolling.
- Responsive columns.
- Detail dialogs.
- Stacked layouts.

Do not shrink important text to unreadable sizes to fit wide tables.

---

## 22. Accessibility

Frontend changes should consider accessibility.

Minimum expectations:

- Form controls have labels.
- Buttons have understandable names.
- Icons used as buttons have accessible labels.
- Keyboard focus remains visible.
- Dialogs manage focus appropriately.
- Error messages are associated with fields.
- Tables use meaningful headers.
- Color is not the only status indicator.
- Interactive elements are reachable by keyboard.
- Text contrast is sufficient.

Use semantic HTML where possible.

Do not turn a non-interactive `<div>` into a button without keyboard and
accessibility behavior.

---

## 23. Date, time and academic-week handling

Date and time handling must be centralized and explicit.

Do not compare localized date strings.

Use stable machine-readable values from the API.

Display Vietnamese labels separately from stored values.

Examples:

```text
MONDAY -> Thứ Hai
MORNING -> Sáng
PENDING -> Chờ duyệt
```

### 23.1. Time zones

Do not assume browser-local time is always the intended academic time zone.

When timestamps are returned by the backend:

- Preserve their offset or timezone meaning.
- Format them consistently.
- Document whether values are UTC or local.

### 23.2. Periods and slots

Do not assume:

- All sessions begin at period 1.
- Every class uses exactly three periods.
- Every week has the same available slots.

Use backend-provided slot definitions.

### 23.3. Week selection

A timetable week selector should use a stable week identifier.

Do not derive academic-week identity only from the displayed date without
confirmed rules.

---

## 24. Internationalization and user-facing text

The primary interface language is expected to be Vietnamese.

Keep user-facing terminology consistent.

Examples:

- “Phòng đào tạo”.
- “Giảng viên”.
- “Lớp học phần”.
- “Khung thời gian”.
- “Ràng buộc cứng”.
- “Ràng buộc mềm”.
- “Yêu cầu điều chỉnh”.

Do not mix different Vietnamese translations for the same domain concept
without reason.

Avoid placing long user-facing strings directly in many components.

A centralized message or localization structure may be introduced when
repetition becomes meaningful.

Do not add a full internationalization framework unless multilingual support
is required.

---

## 25. Security rules

Frontend code is visible to users.

Never place secrets in:

- TypeScript files.
- React components.
- `VITE_` environment variables.
- Static assets.
- Browser storage.
- Source maps.

Do not store:

- Database credentials.
- Private keys.
- Backend signing secrets.
- Administrative passwords.

### 25.1. Browser storage

Do not place sensitive data in browser storage without understanding the
security implications.

Authentication storage strategy must follow the approved backend design.

Do not create a custom token-storage mechanism casually.

### 25.2. Untrusted content

Treat API and uploaded data as untrusted display content.

Avoid rendering raw HTML.

Do not use `dangerouslySetInnerHTML` unless explicitly justified and sanitized.

### 25.3. File downloads

Use backend-provided export responses safely.

Do not construct file content from unvalidated client state when the backend
must provide the official timetable export.

---

## 26. Performance

Do not optimize prematurely.

Before optimizing:

1. Confirm correct behavior.
2. Measure the problem.
3. Identify the expensive render or request.
4. Apply a focused change.
5. Verify the result.

Avoid unnecessary use of:

- `useMemo`.
- `useCallback`.
- React memoization.
- Global state.
- Virtualization.

Use them only when they solve an observed or clearly justified problem.

### 26.1. Rendering

Avoid:

- Expensive calculations inside repeated renders.
- Creating large transformed datasets repeatedly.
- Rendering thousands of rows without controls.
- Unstable props that trigger unnecessary child renders.

### 26.2. Network

Avoid:

- Duplicate requests.
- Requesting complete datasets when filters or pagination exist.
- Polling after a run completes.
- Refetching unchanged reference data unnecessarily.

Performance changes must not compromise correctness or clarity.

---

## 27. State management

Use the simplest appropriate state location.

Possible categories:

- Local component state.
- Feature-level context.
- URL state.
- Server-state library when formally adopted.
- Application-wide authentication state.

Do not put all state into a global store.

Global state should be reserved for truly application-wide concerns, such as:

- Current authenticated user.
- Global authentication status.
- Shared application configuration.

Server data should not be duplicated unnecessarily in local and global state.

Do not introduce Redux or another large state-management library without a
clear project need and approval.

---

## 28. Routing

Routes should reflect user workflows.

Potential routes may include:

```text
/login
/imports
/imports/:batchId
/algorithm/configure
/algorithm/runs/:runId
/timetables/lecturers
/timetables/rooms
/timetables/sections
/my-timetable
/adjustment-requests
/adjustment-requests/:requestId
```

The final route structure must follow actual implementation decisions.

### 28.1. Route protection

Protected routes should:

- Check authentication state.
- Check relevant permission state.
- Handle loading while authentication is being resolved.
- Redirect or display access denied appropriately.

Backend authorization remains mandatory.

### 28.2. Not found

Provide a meaningful not-found page.

Do not silently redirect every unknown route to the home page.

---

## 29. Tables and data presentation

Data tables should support the actual user task.

Consider:

- Stable column headers.
- Sorting where useful.
- Filtering.
- Pagination.
- Loading state.
- Empty state.
- Error state.
- Row actions.
- Accessible headers.
- Responsive overflow.

Do not display internal IDs unless they help the user.

Use domain identifiers such as section codes when they are meaningful.

For validation reports, keep row and column information visible.

---

## 30. Export actions

Export buttons should clearly state:

- Format.
- Scope.
- Current filters or selected timetable.
- Whether the export is being prepared.

Examples:

```text
Xuất CSV
Xuất Excel
Xuất lịch giảng viên
Xuất thời khóa biểu tổng thể
```

Handle:

- Loading state.
- Empty export.
- Server error.
- Unauthorized export.
- Filename from response headers when available.

Do not claim an export succeeded before the response is received.

---

## 31. Frontend testing

Use the configured frontend test tools once available.

Tests should focus on user-observable behavior.

Avoid tests that depend heavily on internal implementation details.

### 31.1. Component tests

Test components for:

- Correct rendering.
- Loading state.
- Empty state.
- Error state.
- User interaction.
- Validation messages.
- Permission-based controls.
- Successful submissions.
- Failed submissions.

### 31.2. Form tests

Test:

- Required fields.
- Invalid numeric ranges.
- Duplicate submission prevention.
- Backend field errors.
- Successful submission.
- Unexpected server failure.

### 31.3. Timetable tests

Test:

- Timetable entries render correctly.
- Empty slots render appropriately.
- Week changes update data.
- Filters affect displayed results.
- Entry details are accessible.
- Unauthorized actions are unavailable.
- Backend-reported conflicts are visible.

### 31.4. Import tests

Test:

- Selecting a valid CSV file.
- Rejecting an unsupported file.
- Upload loading state.
- Preview rendering.
- Multiple validation errors.
- Import confirmation.
- Import failure.

### 31.5. Authorization tests

Test:

- Lecturer navigation.
- Training Department navigation.
- Unauthorized route access.
- Forbidden action handling.
- Authentication expiration behavior.

Do not only test whether a button is hidden; test route and error handling as
well.

### 31.6. API mocking

Mock API boundaries, not internal component functions.

Use realistic request and response shapes.

Do not create mock responses that contradict the documented backend contract.

---

## 32. Frontend commands

Check the actual `package.json` before running commands.

When configured, expected commands may include:

```bash
cd frontend
npm install
```

```bash
cd frontend
npm run dev
```

```bash
cd frontend
npm run lint
```

```bash
cd frontend
npm test
```

```bash
cd frontend
npm run build
```

Do not report a command as successful unless it was actually run.

If a script is not configured, report that fact.

Do not invent script names without updating and documenting `package.json`.

Use the project’s selected package manager consistently.

Do not mix:

```text
npm
yarn
pnpm
```

without an explicit decision.

Commit the appropriate lock file.

---

## 33. Environment configuration

Frontend environment variables should be documented in:

```text
.env.example
```

Possible frontend variable:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Do not commit real environment files.

Do not place secret values in frontend environment variables.

Validate required environment configuration at startup when appropriate.

Fail with a clear development error when a required value is missing.

---

## 34. Error boundaries

Use error boundaries for unexpected render failures when the application
structure justifies them.

An error boundary does not replace:

- API error handling.
- Form validation.
- Loading states.
- Domain error rendering.

Do not wrap every small component in a separate error boundary.

Provide a safe fallback and a way to retry or navigate.

---

## 35. Documentation requirements

When frontend behavior changes, update relevant documentation.

Examples:

- New route.
- New environment variable.
- New role requirement.
- New user workflow.
- New API dependency.
- New setup command.
- New component convention.

Do not describe a planned feature as completed.

Use clear status language:

- Planned.
- In development.
- Implemented.
- Requires confirmation.

Screenshots should not be treated as the only documentation of behavior.

---

## 36. Prohibited actions

Do not:

- Put business rules only in the frontend.
- Call the database directly.
- Hard-code backend URLs in many components.
- Store backend secrets in `VITE_` variables.
- Use `any` without justification.
- Scatter raw status strings throughout the application.
- Use array indexes as keys when stable IDs exist.
- Render raw unsanitized HTML.
- Claim a timetable is valid based on frontend checks.
- Hide backend validation details behind a generic error without reason.
- Add a large UI or state library without approval.
- Duplicate API types inconsistently across features.
- Use color as the only status indicator.
- Make destructive actions without confirmation.
- Leave polling running after completion.
- Claim tests passed without running them.
- Reformat unrelated frontend files in a small PR.
- Implement mobile-specific scope not required by the project.
- Create a visual design system before the project needs it.

---

## 37. Frontend Definition of Done

A frontend task is complete when applicable conditions are satisfied:

- The UI matches the assigned Issue and acceptance criteria.
- Loading, empty, error and success states are handled.
- User input is validated appropriately.
- Backend validation remains authoritative.
- Role-based behavior is represented correctly.
- Protected actions rely on backend authorization.
- API calls use the centralized client.
- Request and response types are defined.
- Components have clear responsibilities.
- Accessibility basics are addressed.
- Relevant tests are added or updated.
- Configured lint, test and build checks pass.
- No secret or machine-specific configuration is committed.
- Documentation is updated when behavior changes.
- Assumptions and unresolved API dependencies are reported.

A screen that only works with one hard-coded response is not complete.

---

## 38. Final report for frontend changes

After modifying frontend files, report:

### Summary

Describe the user-visible behavior that changed.

### Files

List created, modified and deleted files.

### Routes and screens

State:

- Routes added or changed.
- Screens added or changed.
- Permissions involved.

### API impact

State:

- Endpoints consumed.
- Request and response types.
- Mocked or unavailable backend behavior.
- Error handling added.

### UI states

State which of these were handled:

- Loading.
- Empty.
- Error.
- Success.
- Unauthorized or forbidden.

### Verification

List:

- Lint commands.
- Test commands.
- Build commands.
- Manual checks.
- Results.

### Accessibility

State relevant accessibility checks performed.

### Assumptions and risks

List unresolved requirements, backend dependencies or untested behavior.
