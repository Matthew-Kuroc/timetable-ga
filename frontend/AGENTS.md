# Frontend Agent Instructions

## 1. Scope

This file applies to every file inside the `frontend/` directory.

The repository-level `AGENTS.md` also applies. When an instruction in this
file is more specific, follow this file for frontend implementation.

The frontend is responsible for presenting information, collecting user input,
calling backend APIs, and displaying validation results.

The frontend must not become the authoritative implementation of timetable
business rules.

The backend remains authoritative for:

- Authentication and authorization.
- CSV validation.
- Timetable generation.
- Hard-constraint validation.
- Soft-constraint scoring.
- Conflict detection.
- Schedule-adjustment processing.
- Schedule persistence.
- Exported data.

---

## 2. Supported Users

The application has three role types:

- `ADMIN`: Quản trị viên.

- `TRAINING_OFFICE`: Phòng đào tạo.
- `LECTURER`: Giảng viên.

The Administrator interface is limited to approved account and role
management. It must not expose timetable-operation controls unless the user
also has the Training Office role. The system must not provide student,
outside-user or public self-registration access.

Do not introduce another role unless the URS and SRS are formally updated.

For the internship MVP, each account has exactly one role, and the runtime
policy allows one `ADMIN`, one `TRAINING_OFFICE`, and multiple `LECTURER`
accounts. There is no public registration or self-service forgotten-password
workflow. Each Lecturer account is bound to one stable `lecturer_code`.

### Administrator

The Administrator frontend may provide:

- Sign-in and sign-out.
- User-account list, search and status filters.
- Account creation and role assignment.
- Account activation/deactivation.
- Account and authentication audit history.
- Explicit bulk Lecturer provisioning from confirmed lecturer codes.
- One-time temporary-password reset for a Lecturer, with the generated value
  shown only once and never recoverable later.

The frontend must force an account marked `must_change_password` to replace
the temporary password before entering its normal portal. It must not expose
stored password hashes, reuse a shared default password, or offer a public
forgot-password form. An authenticated user may change their own password.

### Training Office

The Training Office frontend may provide:

- Sign-in and sign-out.
- CSV upload, preview, validation, and import.
- Genetic Algorithm configuration.
- Genetic Algorithm execution.
- Full timetable viewing.
- Timetable candidate selection.
- Direct schedule editing.
- Schedule-segment editing.
- Makeup-session creation.
- Lecturer-request review.
- Request approval or rejection.
- Run history and change history.
- CSV and Excel export.

### Lecturer

The Lecturer frontend may provide:

- Sign-in and sign-out.
- Personal weekly timetable.
- Assigned course-section details.
- Schedule-adjustment request creation.
- Submitted-request history.
- Request-status tracking.

A lecturer must not be shown controls that allow them to:

- Create or delete course sections.
- Change the official timetable directly.
- Edit another lecturer's timetable.
- Approve or reject adjustment requests.
- Change the primary lecturer of a course section.
- Reject an assigned course section.

Client-side permission checks improve user experience but are not sufficient
security. The backend must enforce every protected operation.

---

## 3. User-Facing Language

Use Vietnamese for user-facing application text.

Use consistent terms:

| Internal term       | User-facing Vietnamese   |
| ------------------- | ------------------------ |
| Training Office     | Phòng đào tạo            |
| Lecturer            | Giảng viên               |
| Course section      | Lớp học phần             |
| Timetable           | Thời khóa biểu           |
| Time slot           | Khung giờ / Ca học       |
| Schedule segment    | Phân đoạn lịch           |
| Makeup session      | Buổi học bù              |
| Adjustment request  | Yêu cầu điều chỉnh lịch  |
| Hard constraint     | Ràng buộc cứng           |
| Soft constraint     | Ràng buộc mềm            |
| Genetic Algorithm   | Thuật toán Di truyền     |
| Candidate timetable | Phương án thời khóa biểu |
| Theory              | Lý thuyết                |
| Practice            | Thực hành                |
| Integrated          | Lý thuyết – thực hành    |

Do not display raw enum values such as `PENDING`, `INTEGRATED`,
`TRAINING_OFFICE`, or `LARGE_HALL` directly to users.

Centralize enum-to-label mappings.

Example:

    const requestStatusLabels = {
      PENDING: "Chờ duyệt",
      APPROVED: "Đã phê duyệt",
      REJECTED: "Bị từ chối",
      CANCELLED: "Đã hủy",
      APPLIED: "Đã áp dụng",
    };

---

## 4. Frontend Structure

Organize frontend code by feature and responsibility.

A recommended structure is:

    frontend/
    ├── src/
    │   ├── api/
    │   ├── app/
    │   ├── components/
    │   ├── features/
    │   │   ├── auth/
    │   │   ├── data-import/
    │   │   ├── ga-runs/
    │   │   ├── timetables/
    │   │   ├── schedule-adjustments/
    │   │   ├── lecturer-requests/
    │   │   └── exports/
    │   ├── hooks/
    │   ├── layouts/
    │   ├── pages/
    │   ├── routes/
    │   ├── types/
    │   ├── utils/
    │   └── validation/
    └── tests/

Adapt the structure to the selected framework, but preserve separation between:

- API communication.
- Domain and API types.
- Reusable UI components.
- Feature-specific state and logic.
- Page composition.
- Routing and authorization.
- Formatting and display utilities.

Do not create one large component that contains an entire workflow.

---

## 5. API Communication

Centralize backend communication in the API layer.

Do not call `fetch`, `axios`, or another HTTP client directly from many
unrelated components.

Use clearly named API functions such as:

- `uploadCsvFile`
- `previewCsvFile`
- `confirmCsvImport`
- `startGaRun`
- `getGaRunStatus`
- `getTimetableByLecturer`
- `getTimetableByRoom`
- `getTimetableByCourseSection`
- `validateScheduleChange`
- `applyDirectScheduleChange`
- `createAdjustmentRequest`
- `approveAdjustmentRequest`
- `rejectAdjustmentRequest`
- `createMakeupSession`
- `exportTimetable`

Every API workflow must handle:

- Initial state.
- Loading state.
- Successful response.
- Empty result.
- Validation errors.
- Authentication errors.
- Authorization errors.
- Network failures.
- Unexpected server errors.

Do not silently ignore failed requests.

Display structured error messages returned by the backend.

Do not infer complex business conclusions from HTTP status codes alone.

---

## 6. Type Safety

Define explicit types for API contracts and important domain objects.

Examples:

    type UserRole =
      | "ADMIN"
      | "TRAINING_OFFICE"
      | "LECTURER";

    type CourseType =
      | "THEORY"
      | "PRACTICE"
      | "INTEGRATED";

    type RequestStatus =
      | "PENDING"
      | "APPROVED"
      | "REJECTED"
      | "CANCELLED"
      | "APPLIED";

    type TimetableStatus =
      | "DRAFT"
      | "PUBLISHED"
      | "IN_PROGRESS"
      | "COMPLETED"
      | "ARCHIVED";

    type AdjustmentScope =
      | "ONLY_THIS_SESSION"
      | "DATE_RANGE"
      | "FROM_THIS_DATE"
      | "ENTIRE_COURSE";

Avoid `any` for API responses.

Use `unknown` and validate data when an external response has not yet been
verified.

Do not copy backend database models directly when the frontend only needs a
smaller API view model.

Centralize shared enums and labels instead of duplicating strings across pages.

---

## 7. Authentication and Protected Routes

Protected pages must require an authenticated session.

Role-specific pages must verify the current user's role.

Recommended route groups:

    /training-office/*
    /admin/*
    /lecturer/*

When the session expires:

- Clear authenticated frontend state.
- Redirect to the login page.
- Display a clear Vietnamese message when appropriate.

Do not:

- Store plaintext passwords.
- Commit credentials.
- Print tokens to the browser console.
- Include private API keys in frontend source code.
- Assume that hiding a button provides authorization.

---

## 8. Navigation

Navigation must reflect the current role.

### Administrator navigation

Recommended items:

- Quản lý tài khoản
- Phân quyền
- Lịch sử xác thực và thay đổi tài khoản

### Training Office navigation

Recommended items:

- Tổng quan
- Nhập dữ liệu
- Cấu hình thuật toán
- Thực hiện xếp lịch
- Kết quả thời khóa biểu
- Điều chỉnh lịch
- Yêu cầu từ giảng viên
- Lịch sử chạy
- Xuất dữ liệu

### Lecturer navigation

Recommended items:

- Lịch giảng dạy của tôi
- Lớp học phần được phân công
- Gửi yêu cầu điều chỉnh
- Yêu cầu đã gửi

Do not show unauthorized modules merely as disabled items unless the interface
must explicitly explain why access is unavailable.

---

## 9. CSV Upload

The CSV import interface should support:

1. Selecting a data category.
2. Selecting a CSV file.
3. Uploading or parsing the file.
4. Displaying column headers.
5. Displaying preview rows.
6. Displaying validation results.
7. Confirming or cancelling the import.

Possible data categories include:

- Giảng viên.
- Nguyện vọng giảng viên.
- Phân công giảng dạy.
- Lớp học phần.
- Phòng học.
- Khung giờ.
- Lịch học kỳ.
- Thời gian phòng không sử dụng.
- Phân đoạn lịch, when supported.

Validation errors should display:

- File name.
- Row number.
- Column name.
- Invalid value.
- Error reason.

Do not display only a generic message such as:

    Dữ liệu không hợp lệ.

Provide actionable details, for example:

    Dòng 14, cột room_code:
    Không tìm thấy phòng có mã F205.

The frontend may perform basic validation for convenience, but backend
validation remains authoritative.

The project CSV convention is:

- UTF-8 encoding.
- Comma-separated values.
- One header row.
- Documented and stable column names.
- One documented date format.

---

## 10. Genetic Algorithm Configuration

The GA configuration screen should support at least:

- Population size.
- Number of generations.
- Crossover rate.
- Mutation rate.
- Soft-constraint weights.

Pre-fill the accepted experiment baseline: lecturer preferences `10`, room
capacity waste `1`, large-room/small-class `25`, schedule gaps `4`, scattered
days `8`, excess consecutive sessions `6`, and evening/weekend avoidance `5`.
The user may change non-negative values; store and display the run snapshot.

It may also support:

- Execution time limit.
- Random seed.
- Number of generations without improvement.

Use appropriate form controls:

- Integer input for counts.
- Decimal input or slider for rates.
- Clear minimum and maximum values.
- Labels and explanations.

Example:

    Tỷ lệ đột biến
    Giá trị hợp lệ từ 0 đến 1.

Prevent obviously invalid submissions in the interface.

Still display backend validation errors because frontend validation is not
authoritative.

Do not hardcode one parameter configuration as universally optimal.

---

## 11. GA Run Status

A GA run may have states such as:

- Chờ chạy.
- Đang chạy.
- Hoàn thành.
- Thất bại.
- Đã dừng.

The interface should display, when available:

- Run identifier.
- Selected input-data version.
- Start time.
- End time.
- Current status.
- Best fitness or cost.
- Number of hard violations.
- Soft-constraint score.
- Current or final generation.
- Execution time.
- Failure reason.
- Random seed.

Do not display a fake progress percentage when the backend cannot calculate
meaningful progress.

Use a spinner and a message such as `Đang thực hiện xếp lịch` instead.

When a safely stopped run contains a best-so-far result, keep that result
visible.

---

## 12. Timetable Views

The frontend must support timetable views by:

- Lecturer.
- Room.
- Course section.

Lecturers must have a personal weekly view.

A timetable item should show:

- Course name.
- Course-section code.
- Lecturer, when relevant.
- Date or effective date range.
- Day of week.
- Start period.
- End period.
- Room.
- Course type.
- Session status.

Do not rely only on color.

Use labels or icons together with color for statuses such as:

- Bình thường.
- Học bù.
- Tạm ngưng.
- Đã chuyển.
- Ngoại lệ một buổi.

The frontend must handle approximately:

- 20 lecturers.
- 100–200 course sections.
- About 1,500–3,000 dated session occurrences.

Do not load every occurrence when the user only needs one week or one filter.

---

## 13. Teaching Days and Time Slots

Monday through Sunday are valid teaching days.

Do not mark Saturday or Sunday as invalid.

Saturday, Sunday, and evening classes may be shown as less preferred only when
the active GA configuration applies the relevant soft weight and the lecturer
has not explicitly preferred that day or slot. They must not be shown as errors.

The interface may visually distinguish weekends, but weekend classes are
normal valid classes.

Display time slots consistently, for example:

- Tiết 1–3
- Tiết 4–6
- Tiết 7–9
- Tiết 10–12
- Tiết 13–15
- Tiết 1–5
- Tiết 1–6
- Tiết 2–6

A multi-meeting practice/integrated section may also use configured two- or
three-period component slots. Display only slots supplied by the backend; do
not invent a two-period range in the browser.

Do not assume all time slots contain three periods.

Never allow the interface to construct arbitrary invalid ranges such as
periods 3–9.

Only allow configured backend time slots.

---

## 14. Course Types

Supported course types are:

- `THEORY`: Lý thuyết.
- `PRACTICE`: Thực hành.
- `INTEGRATED`: Lý thuyết – thực hành.

An integrated course section:

- Is displayed as one course section.
- Has one primary lecturer.
- Has five or six total weekly periods, possibly declared as one continuous
  meeting or two meetings such as `3+2` or `3+3`.
- Must not be displayed as separate theory and practice course sections or
  pedagogical components. Multiple scheduled meetings remain entries of the
  same `INTEGRATED` section.
- May have consecutive-day meetings because no minimum day gap is required.

Display the required room type separately from the course type.

Example:

    Loại lớp: Lý thuyết – thực hành
    Loại phòng yêu cầu: Phòng máy

Do not assume every integrated course requires a computer laboratory.

The required room type must come from the course-section data.

---

## 15. Lecturer Relationships

The frontend must represent the approved teaching-assignment model correctly.

- Each course section has one primary lecturer.
- One lecturer may teach multiple course sections.
- One lecturer may teach multiple sections of the same course.
- One lecturer may teach different courses in the same semester.
- A lecturer may teach consecutive sessions.
- A lecturer must not have overlapping sessions.

Do not display language implying that a lecturer may teach only one class or
one course.

The frontend does not assign lecturers to courses. Teaching assignments are
provided as input data before timetable generation.

---

## 16. Room Selection

When displaying or selecting a room, show:

- Room code.
- Room name.
- Room type.
- Capacity.
- Availability status.

The interface must distinguish between hard errors and soft warnings.

### Hard error example

    Không thể chọn phòng A301.
    Sức chứa phòng là 40 nhưng sĩ số dùng để xếp lịch là 55.

### Soft warning example

    Phòng F201 có sức chứa 130, lớn hơn đáng kể so với sĩ số lớp là 50.
    Phòng này vẫn có thể được sử dụng nếu Phòng đào tạo xác nhận.

Do not block the Training Office from selecting a large room when:

- The room is available.
- The room type is compatible.
- The room has sufficient capacity.
- No hard conflict exists.

Large rooms should normally be preserved for large classes or used when
standard rooms are unavailable, but this is a soft preference.

Do not add room-to-course restrictions unless they exist in input data.

Do not add a travel-time warning between rooms or buildings.

---

## 17. Academic Calendar and Holidays

The timetable uses actual dates and an academic-calendar mapping.

The frontend may display:

- Semester start date.
- Semester end date.
- Academic week.
- Teaching dates.
- Holidays.
- Non-teaching dates.

When a regular class falls on a holiday:

- Do not display a normal session occurrence.
- Do not automatically display `Tạm ngưng`.
- The calendar may show an empty date or a holiday marker.
- The course-section detail may show that one session still needs to be made up.

Example:

    Số buổi yêu cầu: 15
    Số buổi đã xếp: 14
    Số buổi cần bù: 1

Do not automatically move a holiday session to the next week in frontend code.

---

## 18. Schedule Segments

A course section may use different rooms or schedules in different date ranges.

Example:

    01/09/2026–15/10/2026
    Thứ Hai, tiết 1–3, phòng A303

    16/10/2026–20/12/2026
    Thứ Hai, tiết 1–3, phòng F201

The interface should clearly display every segment's:

- Effective start date.
- Effective end date.
- Day of week.
- Time slot.
- Room.

When editing a repeating schedule, the Training Office should select an
adjustment scope:

- Chỉ buổi này.
- Trong khoảng ngày được chọn.
- Từ ngày này đến hết học phần.
- Toàn bộ lịch cố định.

Display the selected scope clearly before confirmation.

Do not modify all occurrences when the user selected only one occurrence.

The recurring day/time schedule is locked when the official timetable is
published for student registration. After that point, do not offer a whole-
schedule day/time change. The Training Office may still create an audited
room-only segment for a long-term facility problem when the day and time slot
remain unchanged and backend hard validation passes.

Do not independently implement segment-splitting rules in multiple components.
Use backend APIs and shared frontend utilities.

---

## 19. Direct Schedule Adjustment

The Training Office may directly edit the official timetable after receiving
information outside the system.

The adjustment form may include:

- Course section.
- Current session or segment.
- Adjustment scope.
- New date.
- New time slot.
- New room.
- Reason.
- Notes.

Before applying a change:

1. Send the proposed change to the backend for validation.
2. Display hard conflicts.
3. Display soft warnings separately.
4. Require confirmation.
5. Apply only after the backend accepts the change.

Do not reproduce the complete conflict-validation engine in frontend code.

A hard conflict must prevent confirmation.

A soft warning may allow the Training Office to confirm the change.

---

## 20. Lecturer Adjustment Requests

A lecturer may submit an adjustment request for one of their assigned course
sections.

Possible request types include:

- Tạm ngưng một buổi.
- Chuyển một buổi.
- Đổi phòng.
- Đề nghị đổi lịch.
- Đề xuất buổi học bù.

The request form should include:

- Course section.
- Affected session or date range.
- Request type.
- Reason.
- Optional proposed date.
- Optional proposed time slot.
- Optional proposed room.

After submission:

- Show the request identifier.
- Show status `Chờ duyệt`.
- Do not change the official timetable.
- Allow the lecturer to view request history.
- Allow cancellation only when the backend permits it.

The application does not need to find a time when every student is free.

Do not add:

- Student selection.
- Student availability checking.
- Student timetable comparison.
- Automatic scheduling negotiations.

---

## 21. Request Review

The Training Office request-review page should show:

- Lecturer.
- Course section.
- Current timetable.
- Requested change.
- Reason.
- Submission time.
- Validation result.
- Hard conflicts.
- Soft warnings.
- Processing history.

Available actions may include:

- Phê duyệt.
- Điều chỉnh phương án rồi áp dụng.
- Từ chối.
- Ghi chú xử lý.

Do not allow approval before backend validation information is available.

When rejecting a request, require a reason or clearly prompt for one.

Use consistent request statuses:

- `PENDING`: Chờ duyệt.
- `APPROVED`: Đã phê duyệt.
- `REJECTED`: Bị từ chối.
- `CANCELLED`: Đã hủy.
- `APPLIED`: Đã áp dụng.

---

## 22. Makeup Sessions

The Training Office may manually create a makeup session.

The form may include:

- Course section.
- Original missed or suspended session.
- Makeup date.
- Time slot.
- Room.
- Reason.
- Notes.

The frontend must send the proposed session to the backend for conflict
validation before applying it.

The frontend must not automatically choose a date based on student
availability.

Display the relationship between the makeup session and the missed session
when that information is available.

Allow valid configured teaching dates in academic weeks 16–18 even when a
normal 15-week section has ended. Show a clear backend validation error for
week 19 or later.

---

## 23. Forms

Every form should:

- Use visible labels.
- Mark required fields.
- Preserve entered values after validation errors.
- Display field errors near the relevant input.
- Prevent duplicate submission while processing.
- Clearly distinguish primary, secondary, and destructive actions.

Do not use placeholder text as the only field label.

Significant actions should require confirmation, including:

- Applying a timetable candidate.
- Replacing an official schedule.
- Applying a direct schedule change.
- Approving a lecturer request.
- Rejecting a lecturer request.
- Cancelling an active GA run.
- Overwriting imported data.

---

## 24. Loading, Empty, and Error States

Every data-driven screen must define:

- Initial state.
- Loading state.
- Success state.
- Empty state.
- Validation-error state.
- Authorization-error state.
- Server-error state.

Useful empty messages include:

    Chưa có lần chạy thuật toán nào.

    Giảng viên chưa có lịch trong tuần này.

    Không có yêu cầu điều chỉnh đang chờ xử lý.

    Chưa có dữ liệu thời khóa biểu cho bộ lọc đã chọn.

Do not display an empty table without explanation.

Error messages should tell the user what happened and what they can do next.

---

## 25. Tables and Large Data

Tables may contain hundreds of course sections and thousands of dated
occurrences.

Use appropriate techniques:

- Pagination.
- Filtering.
- Sorting.
- Search.
- Server-side queries where appropriate.
- Virtualization when necessary.
- Stable column widths.
- Sticky headers where useful.

Use stable identifiers as row keys.

Do not use array indexes as keys for mutable timetable rows.

Do not request and render the entire semester when the user is viewing only one
week.

---

## 26. Date and Number Formatting

Use a consistent Vietnamese date display format:

    dd/MM/yyyy

Display date ranges as:

    01/09/2026–20/12/2026

Send API dates in the documented API format, normally:

    yyyy-MM-dd

Do not send locale-formatted dates to the backend unless the API explicitly
requires them.

Exported CSV/XLSX date cells use `dd-MM-yyyy` for the confirmed Vietnamese
handoff format; this does not change the ISO API contract.

Display GA rates consistently as either:

- Decimal values such as `0,10`.
- Percentages such as `10%`.

Do not mix the two formats on the same form without explanation.

---

## 27. Accessibility

The frontend should be usable with keyboard navigation.

Provide:

- Associated labels for inputs.
- Visible focus indicators.
- Semantic buttons.
- Accessible table headers.
- Alternative text for meaningful images.
- Text labels in addition to status colors.
- Sufficient contrast.

Modal dialogs should:

- Receive focus when opened.
- Keep focus within the dialog while active.
- Return focus to the triggering element after closing.
- Support keyboard closing when safe.

Do not use clickable `div` elements when a semantic button or link is
appropriate.

---

## 28. Responsive Design

The primary target is a desktop web application.

Still ensure:

- Forms remain usable on smaller screens.
- Tables can scroll horizontally.
- Important actions remain visible.
- Dialogs do not exceed the viewport.
- Navigation remains accessible.

Do not reduce the desktop timetable experience merely to force a complex weekly
calendar into a narrow mobile layout.

---

## 29. Performance

Avoid unnecessary API requests and component re-renders.

Use one consistent server-state approach when a query library is selected.

Do not duplicate large timetable collections across multiple component states.

Prefer backend filtering for large datasets.

Use memoization only when it provides a clear benefit.

Do not optimize prematurely at the cost of readability.

---

## 30. Security and Privacy

Never place secrets in frontend source code.

Frontend environment variables must not contain:

- Database passwords.
- Private API keys.
- Administrative credentials.
- Permanent access tokens.

Do not log:

- Passwords.
- Authentication tokens.
- Sensitive personal information.
- Complete private API responses unnecessarily.

Student accounts and student personal data are outside the current project
scope.

Sample screens and tests must not include real private student data.

---

## 31. Testing

Frontend tests should focus on visible user behavior.

At minimum, test:

- Login success and failure.
- Role-based navigation.
- Protected routes.
- CSV preview.
- CSV validation-error display.
- Invalid GA configuration.
- GA run-status display.
- Timetable filtering.
- Weekend timetable display.
- Theory time-slot labels.
- Practice time-slot labels.
- Integrated-course display.
- Practice/integrated `3+2` multi-meeting display and consecutive-day meetings.
- Room-capacity hard errors.
- Large-room soft warnings.
- Holiday dates without normal sessions.
- Missing-session count.
- Schedule-segment display.
- Editing only one occurrence.
- Editing a date range.
- Direct Training Office adjustment.
- Lecturer-request submission.
- Request approval.
- Request rejection.
- Makeup-session creation.
- Makeup creation in week 18 and rejection in week 19.
- Empty, loading, and error states.

Avoid fragile tests that depend heavily on CSS classes or internal component
implementation.

---

## 32. Code Quality

- Use clear component and function names.
- Keep components focused.
- Extract repeated UI patterns.
- Avoid deeply nested conditional rendering.
- Avoid files containing unrelated features.
- Prefer explicit props and types.
- Remove unused imports.
- Remove dead code.
- Do not commit debugging logs.
- Do not suppress type errors without documenting the reason.
- Centralize labels, enums, route names, and query keys.
- Follow the configured formatter and linter.

Do not add a state-management library unless the project needs it.

Do not create abstractions that are more complicated than the feature they
support.

---

## 33. Scope Protection

Do not create frontend modules for:

- Student accounts.
- Course registration.
- Student individual timetables.
- Tuition.
- Grades.
- Student profiles.
- Automatic student-availability checking.
- Automatic email, SMS, or push notifications.
- Automatic lecturer-to-course assignment.
- Practical-class group splitting.
- Multiple primary lecturers for one course section.
- Guaranteed globally optimal timetable generation.

When a requested screen implies a new business requirement, update the URS and
SRS before implementing it.

---

## 34. Definition of Done

A frontend change is complete when:

- It follows the latest URS and SRS.
- It respects role permissions.
- It uses typed API contracts.
- It handles loading, success, empty, and error states.
- It does not duplicate authoritative backend business logic.
- User-facing text is clear and consistent in Vietnamese.
- It supports keyboard use where applicable.
- It includes appropriate tests.
- It contains no secrets or private sample data.
- Formatting, linting, type checking, and tests pass.
