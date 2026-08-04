# Repository Agent Instructions

## 1. Purpose

This repository contains the internship project:

**Teaching Timetable Scheduling Application Using Genetic Algorithm**

The system is a web application that supports:

- Importing timetable input data from CSV files.
- Validating and normalizing input data.
- Configuring and running a Genetic Algorithm.
- Generating teaching timetable candidates.
- Viewing timetables by lecturer, room, and course section.
- Manually adjusting schedules with conflict validation.
- Processing lecturer schedule-change requests.
- Exporting results to CSV and Excel.

Keep all implementations within the approved internship-project scope.

---

## 2. Instruction Scope and Precedence

This file applies to the entire repository.

More specific instructions may exist in nested files:

- `backend/AGENTS.md`
- `backend/app/algorithms/genetic/AGENTS.md`
- `frontend/AGENTS.md`

When instructions conflict, the closest `AGENTS.md` to the modified file takes precedence.

The latest approved URS and SRS documents are the primary business-requirement sources. When requirements conflict:

1. Use the latest approved URS/SRS version.
2. Prefer explicit business decisions over earlier assumptions.
3. Do not invent missing requirements.
4. Record unresolved issues in the requirements documentation before implementation.

Before starting a new implementation session, read
`docs/backlog/TKB-001-to-TKB-005.md` for the current technical handoff and
prioritized backlog. It is not a replacement for the URS/SRS.

---

## 3. Approved System Users

The runtime application now defines three roles: `ADMIN`, `TRAINING_OFFICE`
and `LECTURER`. The three-role expansion is recorded in the draft URS/SRS and
remains subject to supervisor confirmation.

### Administrator

The Administrator may:

- Sign in using an account provisioned by an existing Administrator.
- Create, update, activate or deactivate approved user accounts.
- Assign `ADMIN`, `TRAINING_OFFICE` or `LECTURER` roles.
- View account and authentication audit history.

The Administrator must not automatically receive timetable-operation access
unless the account is also explicitly granted the Training Office role.

The system must not provide student accounts, public self-registration or
login access for outside users.

### Training Office

The Training Office may:

- Sign in.
- Import and validate CSV data.
- Configure and run the Genetic Algorithm.
- View all timetable results.
- Select a timetable candidate for use.
- Directly edit a timetable.
- Review lecturer adjustment requests.
- Approve, reject, or modify proposed changes.
- Add makeup sessions manually.
- Export timetable data.
- View execution and change history.

### Lecturer

A lecturer may:

- Sign in.
- View their personal timetable.
- View details of assigned course sections.
- Submit schedule-adjustment requests.
- Track the processing status of submitted requests.

A lecturer must not:

- Create or delete course sections.
- Change the official timetable directly.
- Approve their own request.
- Modify another lecturer's timetable.
- Reject an assigned course section.

Do not add any role beyond `ADMIN`, `TRAINING_OFFICE` and `LECTURER` unless the
requirements are formally changed again.

---

## 4. Teaching Assignment Rules

Teaching assignments are prepared before timetable generation.

The Genetic Algorithm does not decide which lecturer teaches which course.

The following rules apply:

- Each course section has exactly one primary lecturer.
- A lecturer may teach multiple course sections.
- A lecturer may teach multiple sections of the same course.
- A lecturer may teach different courses in the same semester.
- A lecturer may teach consecutive sessions.
- A lecturer must not teach overlapping sessions.
- Practical classes are not split into student groups.
- A course section is not jointly assigned to multiple primary lecturers.

A substitute lecturer for one exceptional session, when supported later, does not replace the primary lecturer of the course section.

---

## 5. Course-Section Schedule Model

Under the current agreed model:

- Each course section has one regular meeting per week.
- A course section may contain approximately 15 occurrences in a semester.
- A dataset of 100–200 course sections may therefore produce roughly 1,500–3,000 dated occurrences.

For the MVP Genetic Algorithm:

- One gene represents the base weekly assignment of one course section.
- A gene selects the day, time slot, and room.
- The lecturer and course section are fixed by teaching-assignment data.
- Dated session occurrences are generated after the base timetable is created.

Do not model every dated occurrence as an independent GA gene unless a documented design decision changes this approach.

---

## 6. Course Types and Period Rules

Supported course types are:

- `THEORY`
- `PRACTICE`
- `INTEGRATED`

### Theory

Theory classes normally use one three-period session.

Configured theory slots may include:

- Periods 1–3
- Periods 4–6
- Periods 7–9
- Periods 10–12
- Periods 13–15

### Practice

Practice classes use five or six periods.

Current valid practice slots are:

- Periods 1–5
- Periods 1–6
- Periods 2–6

### Integrated theory and practice

An integrated course:

- Is one course section.
- Is taught by one lecturer.
- Combines theory and practice in the same session.
- Uses five or six periods.
- Uses the same time-slot rules as a practice class.
- May require a computer laboratory, specialized room, or normal theory room depending on input data.

Do not infer the required room type only from the course type. Use the explicit room requirement of the course section.

Never generate arbitrary period ranges. All generated schedules must use configured valid time slots.

A session must remain inside one valid teaching block. Do not create schedules that cross the break between morning and afternoon sessions.

---

## 7. Teaching Days and Lecturer Preferences

Monday through Sunday are valid teaching days.

Saturday, Sunday, and evening slots remain valid teaching times. The default
quality policy may apply configurable soft avoidance weights to these times
because they are normally less preferred.

An explicit lecturer preferred day or preferred slot must override the default
avoidance for that lecturer. The GA may still use these slots when they are the
best feasible option; this is never a hard-constraint violation.

Lecturer preferences are soft constraints and may include:

- Preferred teaching days.
- Preferred time slots.
- Undesired teaching days.
- Undesired time slots.
- Preference for compact teaching days.
- Preference to reduce long gaps between sessions.

Do not assume a lecturer's unexpected future absence is known before course registration.

Only treat an unavailable slot as a hard constraint when the input explicitly marks it as a confirmed fixed restriction.

---

## 8. Room Rules

Every room has its own:

- Room code.
- Room type.
- Physical capacity.
- Availability status.
- Optional unavailable dates or time slots.

A room assignment is valid only when:

- The room is not occupied by another class at the same time.
- The room type satisfies the course-section requirement.
- The room capacity is greater than or equal to the scheduling student count.
- The room is available during the applicable date range.

The scheduling student count should use:

1. The approved maximum student count, when available.
2. Otherwise, the initial registration limit.
3. Otherwise, the expected student count.

An approved registration limit must never exceed the physical capacity of the assigned room.

### Large rooms

Large lecture halls, including rooms with approximately 130 seats:

- Are not restricted to general-education courses.
- May be used by any compatible course section.
- May be used for manual schedule changes or makeup sessions.
- Should normally be preserved for large classes or used when standard rooms are unavailable.

For automatic scheduling, prefer a standard room whose capacity is reasonably close to the class size.

Using a large hall for a small class is a soft-constraint violation, not a hard-constraint violation.

The Training Office may manually confirm a large room when all hard constraints are satisfied.

Do not add a travel-time constraint between rooms or buildings. Official time slots already provide sufficient transition time.

---

## 9. Academic Calendar and Holidays

The timetable uses actual dates together with an academic-calendar mapping.

The academic calendar should identify:

- Semester start date.
- Semester end date.
- Academic week number.
- Teaching days.
- Holidays and non-teaching days.

When a regular class date falls on a holiday:

- Do not generate a normal session occurrence for that date.
- Do not display the session as `SUSPENDED`.
- Treat the date as empty.
- Record that the course section may be missing one required session.
- Allow the Training Office to add a makeup session manually later.

Do not automatically move every holiday session to the next week.

A course is considered complete when its regular and makeup sessions satisfy the required number of sessions or periods.

---

## 10. Schedule Segments and Exceptions

A course section may use different rooms during different date ranges.

Example:

- From the semester start to 15 October: room A303.
- From 16 October to the semester end: room F201.

The data model must support schedule segments containing:

- Effective start date.
- Effective end date.
- Day of week.
- Time slot.
- Room.

For the MVP:

- The Genetic Algorithm creates one base schedule for the course section.
- The Training Office may manually split the schedule into date-range segments.
- The Genetic Algorithm does not need to create multiple room segments automatically.

The system should support adjustment scopes such as:

- One specific session.
- A selected date range.
- From a selected date to the end of the course.
- The entire regular schedule before the registration lock point.

A one-session exception takes precedence over the base segment for that date.

---

## 11. Schedule Adjustments

The system supports two adjustment paths.

### Direct adjustment

A lecturer may contact the Training Office outside the system.

The Training Office then directly edits the official timetable.

### Lecturer request

A lecturer may submit an adjustment request in the application.

The request may include:

- Affected course section or session.
- Request type.
- Reason.
- Proposed date.
- Proposed time slot.
- Proposed room.

The request must not change the timetable until the Training Office processes it.

Typical request states are:

- `PENDING`
- `APPROVED`
- `REJECTED`
- `CANCELLED`
- `APPLIED`

Every applied change must be traceable.

Before applying a change, validate all hard constraints.

The system does not need to find a time when every student is free. The lecturer, students, and Training Office resolve that issue outside this application.

---

## 12. Hard Constraints

A timetable candidate or manual adjustment is invalid when it violates any of the following:

- A lecturer teaches overlapping classes.
- A room hosts overlapping classes.
- A room type does not satisfy the course-section requirement.
- Room capacity is smaller than the scheduling student count.
- A time range is not a configured valid slot.
- A session crosses an invalid teaching-block boundary.
- A session is outside the semester or applicable date range.
- A room is unavailable for the selected date and time.
- A confirmed fixed lecturer restriction is violated.
- Required schedule information is missing.
- Two effective schedule segments create contradictory schedules for the same occurrence.

Hard-constraint violations must not be silently accepted.

Return a clear and actionable validation message.

---

## 13. Soft Constraints

Soft constraints influence timetable quality but do not make a timetable invalid.

Examples include:

- Lecturer day and time preferences.
- Reducing long gaps between a lecturer's sessions.
- Avoiding unnecessarily scattered teaching days.
- Maintaining a reasonably balanced teaching distribution.
- Preferring weekdays and daytime sessions when no lecturer-specific preference applies.
- Selecting rooms with capacity close to the class size.
- Preserving large lecture halls when suitable standard rooms remain available.
- Keeping a stable regular schedule for each course section.

Do not make Saturday, Sunday, or evening sessions invalid solely because of
their time. Their avoidance weights must be configurable and recorded with
each GA run.

Soft-constraint weights must be configurable and recorded with each GA run.

---

## 14. CSV Data Rules

The team defines the CSV schemas used by the project.

Default CSV requirements:

- UTF-8 encoding.
- Comma-separated values.
- A header row.
- Stable unique identifiers.
- Explicit and documented field names.
- Dates in one documented format.
- No silent conversion of invalid values.

The Training Office prepares one complete seven-file CSV batch in Excel and
uploads it to the application. After preview and validation, only an explicitly
confirmed batch is persisted and eligible for a GA run. The `official` sample
directory is a development/test fixture and must not be the normal runtime
input source.

The input model may include:

- Lecturers.
- Lecturer preferences.
- Course sections and teaching assignments.
- Rooms.
- Room availability.
- Time slots.
- Academic calendar dates.
- Optional schedule segments.
- Optional adjustment requests.

CSV validation errors must identify:

- File.
- Row.
- Column.
- Invalid value.
- Reason.

Do not include real student personal data in sample files.

---

## 15. Out-of-Scope Features

Do not implement the following unless the approved requirements change:

- Student accounts.
- Course registration.
- Tuition, grades, or student profiles.
- Individual student timetables.
- Finding a makeup time from every student's availability.
- Automatic negotiation between lecturers and students.
- Automatic email, SMS, or push notifications.
- Automatic lecturer-to-course assignment.
- Practical-class student-group splitting.
- Multiple primary lecturers for one course section.
- Full production integration with the university management system.
- Guaranteed globally optimal GA results.

---

## 16. Implementation Principles

- Keep business rules out of UI components.
- Centralize validation so GA generation and manual editing use the same rules.
- Keep the GA module independent of HTTP and database frameworks.
- Prefer explicit types, enums, and domain objects over unstructured dictionaries.
- Keep functions small and focused.
- Avoid duplicated business-rule implementations.
- Preserve old data and run history when creating a new timetable candidate.
- Use deterministic random seeds in algorithm tests.
- Add tests whenever a business rule is added or changed.
- Do not silently relax a hard constraint to obtain a timetable.
- Do not expand the project scope without updating URS/SRS first.

---

## 17. Testing Expectations

At minimum, tests should cover:

- Lecturer-overlap detection.
- Room-overlap detection.
- Partial period overlap, such as periods 1–5 versus 2–6.
- Room-type compatibility.
- Room-capacity validation.
- Valid and invalid time slots.
- Weekend scheduling.
- Lecturer preference scoring.
- Large-room soft penalties.
- Holiday occurrence generation.
- Missing-session calculation.
- Schedule-segment splitting.
- One-session exceptions.
- Direct timetable edits.
- Lecturer-request approval and rejection.
- CSV validation.
- Deterministic GA execution with a fixed seed.

Start with small datasets that can be checked manually.

The initial target dataset is approximately:

- 20 lecturers.
- 100–200 course sections.
- About 15 regular occurrences per course section.
- Approximately 1,500–3,000 generated dated occurrences.

---

## 18. Documentation and Change Discipline

When modifying a business rule:

1. Check the latest URS and SRS.
2. Update documentation before or together with the code.
3. Update related sample CSV files.
4. Update validation rules.
5. Add or update tests.
6. Record assumptions that still require confirmation.

Use Vietnamese for user-facing application text and project requirement documents unless an existing file explicitly uses another language.

Never commit:

- Passwords.
- API keys.
- Access tokens.
- `.env` files containing secrets.
- Real private student data.
- Generated build artifacts.
- Large temporary experiment files without approval.
