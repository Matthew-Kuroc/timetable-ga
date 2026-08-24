# User Requirements Specification

## 1. Document Information

| Field | Value |
| --- | --- |
| Project | Teaching Timetable Scheduling Application Using Genetic Algorithm |
| Document | User Requirements Specification (URS) |
| Source file | `D:\DoAn\DuAn\TaiLieu_UR.docx` |
| Version | 0.3 draft |
| Created | 09/07/2026 |
| Updated | 23/08/2026 |
| Status | Draft; MVP business decisions confirmed by the project owner, final delivery/demo pending supervisor confirmation |

## 2. Purpose

This document describes user needs, expectations and usage boundaries for the teaching timetable scheduling application. It is written from a business and user perspective so the supervisor and project team can confirm scope before implementation and before finalizing the SRS.

This document does not define source code structure, database tables, API details or exact implementation of Genetic Algorithm operators.

## 3. Business Context

Faculties provide lecturer assignment and course-section data to the Training Department. The Training Department must place a large number of course sections into suitable rooms and time slots while avoiding conflicts.

The system is needed because manual scheduling becomes time-consuming and difficult to control when the number of lecturers, rooms and course sections increases. Users need a web application to import data, run a Genetic Algorithm, view schedules, handle change requests and export results.

## 4. User Goals

1. Reduce time and manual effort for timetable creation.
2. Generate timetable options that do not violate confirmed hard constraints.
3. Improve soft preferences such as lecturer preferred time slots, gaps and weekly distribution.
4. Allow the Training Department to view schedules by lecturer, room and course section.
5. Allow lecturers to view their weekly personal timetable and submit allowed change requests.
6. Ensure official schedule changes are applied only after conflict checking and authorized approval.
7. Export results to CSV or Excel and keep information needed for experiments.

## 5. Stakeholders

| Stakeholder | Main needs | Responsibility / limitation |
| --- | --- | --- |
| Administrator | Provision and manage accounts; assign roles; activate or deactivate access. | Does not operate timetable generation or change timetable data unless explicitly granted the Training Department role. |
| Training Department / Manager | Import and validate data; configure and run GA; view all schedules; handle change requests; export results. | May apply changes only after valid data and hard constraints are checked. |
| Lecturer | Log in; view personal weekly timetable; view class details; submit and track suspend/move requests. | Cannot add classes, delete classes, reject classes, directly edit official timetables or view another lecturer's personal schedule. |
| Faculty | Provide teaching assignment data and related information. | In the internship version, may only be a data provider and may not need a dedicated account. |
| Supervisor / tester | Provide sample data, test functions, evaluate algorithm results and confirm requirements. | May not be a regular system operator. |
| Student team | Analyze, design, implement, test, document and deliver the product. | Must not invent unconfirmed business rules. |

## 6. Product Scope

### 6.1 In Scope

- Desktop web application.
- Login and role-based access control.
- Administrator account provisioning and user/role management; no public, student or external-user login.
- The bootstrap Administrator identity is a protected system account and cannot be edited or deactivated through normal account management.
- Each lecturer receives an individual provisioned account linked to a confirmed-batch lecturer code and sees only that lecturer's timetable.
- CSV import, preview, validation and storage for teaching assignments, rooms, time slots and additional constraints.
- Genetic Algorithm configuration and execution.
- Hard-constraint checking and soft-constraint evaluation.
- Schedule views by lecturer, room and course section.
- Lecturer weekly personal timetable.
- Suspend or move timetable requests within confirmed rules.
- Re-run GA, save results and choose a timetable option.
- Export timetable to CSV or Excel.
- Testing with small, medium and real/supervisor-provided datasets.

### 6.2 Out of Scope

- Student course registration.
- Tuition, grade or student profile management.
- Official integration with the full university management system without a provided API/specification.
- Email, SMS or push notifications unless added to scope.
- Guaranteeing global optimal solutions for every dataset.
- Production deployment for the entire university during the internship period.

## 7. Implementation Levels

| Level | Content |
| --- | --- |
| Required MVP | Upload and validate CSV; configure and run GA; handle hard constraints; view timetable; adjust at least one session; export CSV or Excel. |
| Complete version | Login, authorization, personal timetable, request-approval workflow, run history and official timetable selection. |
| Extended version | Flexible column mapping, downloadable error reports, compare multiple options, reproducible seed, advanced logs/audit and automatic notifications. |

## 8. Proposed Business Processes

### 8.1 Current Process

| Step | Description |
| --- | --- |
| 1 | Faculties prepare and send lecturer assignment data to the Training Department. |
| 2 | The Training Department consolidates course-section, lecturer, room and time-slot data. |
| 3 | The timetable manager schedules manually or with separate support tools. |
| 4 | Conflicts are checked and room/time selections are adjusted. |
| 5 | The timetable is issued for downstream management processes. |

### 8.2 Proposed System Process

| Step | Description |
| --- | --- |
| 1 | Training Department logs in and uploads required CSV files. |
| 2 | System previews and validates structure, data types and references. |
| 3 | Training Department fixes invalid data or confirms a valid import batch. |
| 4 | Training Department configures GA parameters and soft-constraint weights. |
| 5 | System runs GA, updates status and stores the best option. |
| 6 | Training Department views results by lecturer, room and course section, including metrics and soft violations. |
| 7 | Training Department re-runs GA if needed and selects the option to use. |
| 8 | Lecturer logs in, views weekly personal timetable and submits change requests if needed. |
| 9 | Training Department checks, approves or rejects requests; system updates only valid approved changes. |
| 10 | Training Department exports timetable to CSV or Excel. |

### 8.3 Proposed Change-Request Process

| Step | Lecturer | Training Department / System |
| --- | --- | --- |
| 1 | Selects a class or session assigned to them. | System checks access rights. |
| 2 | Selects request type, enters reason and proposed option if available. | System checks required fields and business deadline. |
| 3 | Confirms submission. | Creates a Pending request; official timetable is unchanged. |
| 4 | Tracks request status. | Training Department views details and requests conflict checking. |
| 5 | Receives result. | Approves or rejects; if approved, updates schedule/status and stores history. |

## 9. User Requirements

Priority values: Must, Should, Could. Status values: Identified, Team proposal,
Confirmed for MVP, Needs supervisor confirmation.

### 9.1 Authentication and Authorization

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-AUTH-01 | Users need to log in with a valid account before accessing protected features. | Must | Identified |
| UR-AUTH-02 | The system must support three roles: Administrator, Training Office and Lecturer, with separate permissions and navigation. The MVP allows one Administrator, one Training Office account and multiple Lecturer accounts, with exactly one role per account. | Must | Confirmed for MVP 23/08/2026 |
| UR-AUTH-03 | Administrators need to create, update, activate/deactivate and assign roles to approved user accounts. | Must | Team proposal |
| UR-AUTH-04 | The system must reject students, unprovisioned accounts and outside users; there is no public self-registration. | Must | Team proposal |
| UR-AUTH-05 | Lecturers may only view their personal timetable and operate on classes assigned to them. | Must | Identified |
| UR-AUTH-06 | Lecturers must not directly add classes, delete classes, reject classes or edit timetable data. | Must | Identified |
| UR-AUTH-07 | Users need to log out and end a session safely. | Must | Team proposal |
| UR-AUTH-08 | Administrator needs to provision Lecturer accounts in bulk from a confirmed lecturer catalog, for selected lecturer codes or the complete batch. Importing lecturer rows alone must not create accounts. | Must | Confirmed for MVP 24/08/2026 |
| UR-AUTH-09 | Each bulk-provisioned Lecturer account must receive a unique random temporary password. The database stores only its hash; a local ignored handoff file may expose the temporary value once to the Administrator. A shared default password is forbidden. | Must | Confirmed for MVP 24/08/2026 |
| UR-AUTH-10 | A user signing in with a temporary password must replace it before accessing the normal role portal. | Must | Confirmed for MVP 24/08/2026 |
| UR-AUTH-11 | Administrator needs to issue a new temporary password when a Lecturer loses access. Reset revokes existing sessions, requires another first-login password change and creates an audit event; the old password cannot be viewed or recovered. | Must | Confirmed for MVP 24/08/2026 |
| UR-AUTH-12 | An authenticated user needs to change their own password after supplying the current password. There remains no public or self-service forgotten-password workflow. | Must | Confirmed for MVP 24/08/2026 |

### 9.2 Data Import and Management

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-DATA-01 | Training Department needs to upload one complete seven-file CSV batch exported from Excel for teaching assignments, rooms, time slots, calendar and additional constraints. | Must | Clarified from internship topic |
| UR-DATA-02 | Training Department needs to preview headers and sample rows before saving. | Must | Identified |
| UR-DATA-03 | Users need clear row, column, value and reason messages when data is invalid. | Must | Identified |
| UR-DATA-04 | Invalid data must not be passed to the algorithm before being fixed or confirmed according to rules. | Must | Identified |
| UR-DATA-05 | Training Department needs to confirm a valid batch before saving it. Editing a saved batch creates a new version instead of changing data used by an earlier run. | Must | Clarified from internship topic |
| UR-DATA-06 | Training Department needs to choose the confirmed dataset batch for each GA run; the sample dataset is only for development and demonstration. | Must | Clarified from internship topic |
| UR-DATA-07 | When real files use different column names, users need a mapping option or clear instructions to fix the file. | Should | Needs supervisor confirmation |
| UR-DATA-08 | Training Department should be able to download an error report for offline correction. | Should | Team proposal |

### 9.3 Genetic Algorithm Configuration and Run

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-GA-01 | Training Department needs to configure population size, number of generations, crossover rate and mutation rate. | Must | Identified |
| UR-GA-02 | Training Department needs to configure priorities or weights for soft constraints, including avoidance of evening, Saturday and Sunday slots. The accepted baseline is documented in the SRS and stored with each run. | Must | Confirmed for MVP 23/08/2026 |
| UR-GA-03 | The system may run only when required data is available and must show missing data reasons. | Must | Identified |
| UR-GA-04 | The system needs to generate a timetable option or report failure with a reason. | Must | Identified |
| UR-GA-05 | Users need to know whether a run is pending, running, completed, failed or stopped. | Must | Identified |
| UR-GA-06 | The system should keep the best option found when a run finishes or is stopped safely. | Should | Team proposal |
| UR-GA-07 | Training Department needs to re-run the algorithm without losing previous results. | Must | Identified |
| UR-GA-08 | Users need to view basic metrics such as run time, fitness and violation counts by group. | Should | Team proposal |

### 9.4 Timetable View and Search

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-VIEW-01 | Training Department needs to view timetables by lecturer. | Must | Identified |
| UR-VIEW-02 | Training Department needs to view room usage schedules. | Must | Identified |
| UR-VIEW-03 | Training Department needs to view all sessions of a course section. | Must | Identified |
| UR-VIEW-04 | Lecturers need to view personal timetable as a weekly calendar and switch weeks. | Must | Identified |
| UR-VIEW-05 | Each calendar item needs to show or open details for course, section, date/week, slot/period and room. | Must | Identified |
| UR-VIEW-06 | Users should be able to filter by lecturer, room, section, date or week. | Should | Team proposal |
| UR-VIEW-07 | Training Department should see the count and type of soft violations for an option. | Should | Team proposal |
| UR-VIEW-08 | Lecturer timetable should be presented in a personal weekly calendar with week navigation, session details and clear empty/loading/error states. | Must | Team proposal |

### 9.5 Timetable Change Requests

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-REQ-01 | Lecturers need to request suspension or movement of one assigned session. | Must | Identified |
| UR-REQ-02 | A whole recurring day/time change is allowed only before the timetable is officially published for student registration. After publication, a long-term facility problem may be handled by an audited room-only segment that preserves the day and time slot. | Must | Confirmed for MVP 23/08/2026 |
| UR-REQ-03 | A request needs to record section, affected session/timetable, request type, reason and proposed option if any. | Must | Team proposal |
| UR-REQ-04 | A submitted request must not change the official timetable until processing is complete. | Must | Needs supervisor confirmation |
| UR-REQ-05 | Training Department needs to view details, check conflicts, approve or reject requests. | Must | Needs supervisor confirmation |
| UR-REQ-06 | Changes that cause lecturer conflict, room conflict, wrong room type, wrong capacity or wrong week must be rejected. | Must | Identified |
| UR-REQ-07 | If a request is rejected, the timetable must remain unchanged and the lecturer must see the reason. | Must | Team proposal |
| UR-REQ-08 | Lecturers need to track requests they submitted. | Must | Team proposal |
| UR-REQ-09 | Lecturers must not approve their own requests or change another lecturer's timetable. | Must | Team proposal |
| UR-REQ-10 | The system should keep handler, time and result history for every request. | Should | Team proposal |

### 9.6 Export, Audit and Delivery

| Code | Requirement | Priority | Status |
| --- | --- | --- | --- |
| UR-EXP-01 | Training Department needs to export the timetable to CSV. | Must | Identified |
| UR-EXP-02 | Training Department needs to export the timetable to Excel `.xlsx`. | Must | Identified |
| UR-EXP-03 | Users should choose export scope: full option, lecturer, room or course section. | Should | Team proposal |
| UR-EXP-04 | Dated CSV/XLSX exports use `DD-MM-YYYY`, CSV uses UTF-8 BOM, and the filename contains batch name, run/official code and timestamp. | Should | Confirmed for MVP 23/08/2026 |
| UR-AUD-01 | Each run should store input data, configuration, time, result and evaluation metrics. | Should | Team proposal |
| UR-AUD-02 | Training Department should view previous runs without losing the current selected option. | Should | Team proposal |
| UR-DEL-01 | Delivery package needs source code, installation guide, sample data, report, experiment results and demo video. | Must | Identified |

## 10. Business Rules

### 10.1 Hard Constraints

- A lecturer must not teach two classes at the same time.
- A room must not host two classes at the same time.
- Every course section must receive the required number of sessions.
- Each session must use a valid time slot.
- Room type must match the course-section requirement.
- Room capacity must be greater than or equal to the scheduling student count.
- A lecturer must not be scheduled in an officially confirmed fixed restriction. Lecturer self-declared unavailable or undesired times before course registration are treated as soft preferences unless confirmed by the Training Department.
- A room must not be scheduled in an unavailable slot.
- Every session must have a course section, lecturer, room and time slot.
- Regular sessions must stay within the course section's normal teaching dates.
- A suspended regular occurrence counts as one missing required session.
- A manually arranged make-up session may be scheduled on a valid teaching
  date in academic week 16, 17 or 18 even when the regular course section ends
  after week 15. Academic week 19 and later are outside the current make-up
  window because they are reserved for process-mark entry.
- Every make-up session must still pass lecturer, room, capacity, room-type,
  configured-slot and fixed-restriction validation.
- Timetable change requests may be applied only after approval and must not introduce new hard-constraint violations.

### 10.2 Soft Constraints

- Prefer lecturer desired time slots.
- Avoid too many consecutive sessions for one lecturer.
- Reduce gaps between sessions in the same day.
- Distribute teaching load reasonably across the week.
- Prefer weekday and daytime sessions through configurable soft weights when no lecturer-specific preference applies. Saturday, Sunday and evening sessions remain valid and may be selected when necessary.
- Do not penalize a Saturday, Sunday or evening slot for a lecturer who explicitly prefers that day or slot.
- Prefer rooms whose capacity is close to class size to reduce waste.
- Avoid frequent campus changes for one lecturer when campus data exists.
- Keep sessions of the same course section stable where possible.

### 10.3 Capacity Rule

Room capacity is treated as a physical limit. Capacity checking uses `scheduling_student_count`, with priority:

1. `approved_max_students`
2. `initial_registration_limit`
3. `expected_students`

The SRS draft marks this rule as clarified, while the UR draft still lists it as a topic to confirm. Until documents are finalized, implementations should keep this logic centralized and easy to change.

## 11. Input Data Groups

| Group | Description |
| --- | --- |
| Course sections | Course code/name, section code, lecturer, number of sessions, weekly meeting count, periods per meeting, student counts, type, weeks and optional campus/notes. The input, not the GA, declares whether a section has more than one weekly meeting. |
| Rooms | Room code/name, capacity, room type, campus, availability and unavailable slots. |
| Time slots | Slot code, day of week, start period, end period, session type and active flag. |
| Lecturers | Lecturer code/name, preferred slots, undesired slots and optional workload preferences. Officially confirmed fixed restrictions may be recorded separately by the Training Department. |
| Additional constraints | Rules or preferences not represented in the core CSV groups. |

## 12. Expected Data Validation

- CSV file must be readable.
- Required columns must exist.
- Required identifiers and fields must not be blank.
- Numeric values must be valid and positive when required.
- Lecturer, room and time-slot references must exist.
- Course-section codes must not duplicate within the same dataset.
- Course types and room types must be in allowed lists.
- Time slots must be valid active slots.
- Error reports should include row, column, value and reason.
- Users must confirm before overwriting existing import data.

## 13. Non-Functional Expectations

- The interface should use Vietnamese terminology consistently.
- Normal search/view operations should respond within a reasonable time for initial test data.
- Uploaded files must be checked for safe file type, size and names.
- Passwords must not be stored in plain text if authentication is implemented.
- Authorization must be enforced by backend APIs, not only by hiding frontend controls.
- The GA module should be independent from frontend and API layers.
- Important data and algorithm behavior should have tests.

## 14. Acceptance Criteria

- Users can import valid CSV data and see clear validation errors for invalid data.
- The system can run GA on a small dataset and produce a timetable with no hard-constraint violations.
- Training Department can view timetable by lecturer, room and course section.
- Lecturer can view personal weekly timetable.
- At least one session change workflow can be submitted, checked and applied or rejected correctly.
- Timetable can be exported to CSV or Excel.
- Administrator can provision an approved account and assign one of the three roles; students and outside users cannot log in.
- Each role sees only its permitted portal and operations.
- Lecturer can use a weekly calendar, view assigned sessions and submit a timetable-change request.
- Experiment metrics can be collected for at least small and medium datasets.

## 15. Project Decisions Recorded on 23/08/2026

These decisions were supplied by the project owner for the internship MVP and
are recorded so later implementation sessions do not invent a different rule.
They remain part of the draft until the supervisor signs off the final URS/SRS.

- A suspension caused by lecturer absence, an unexpected conflict or a missed
  class creates one missing required session.
- Lecturer and Training Department coordinate the replacement outside the
  automatic scheduler; the Training Department records the make-up session in
  the application after hard-constraint validation.
- A section with 15 regular teaching weeks may use academic weeks 16-18 for
  make-up teaching. Week 19 and later are not allowed under the current rule.
- No real university CSV was supplied. The team-defined seven-file schema and
  anonymized fixtures are the approved MVP input contract, but are not claimed
  to be a production integration format.
- Most course sections have one weekly meeting. A `PRACTICE` or `INTEGRATED`
  section may have two weekly meetings when this is explicitly declared in the
  final input. A three-period `THEORY` section normally remains one weekly
  meeting. The GA must schedule declared meetings and must not decide to split
  a course by itself.
- Example: an integrated NoSQL section may have one three-period meeting on
  Monday periods 10-12 and a second three-period meeting on Thursday periods
  7-9. A five-period section is normally split `3+2`. These meetings remain
  entries of the same `INTEGRATED` section, not separate theory/practice parts.
- Two declared weekly meetings have no minimum spacing requirement and may be
  scheduled on consecutive days.
- The seven-file schema uses `weekly_sessions`, `periods_per_session` for the
  first/only meeting, and optional `second_session_periods`. The system derives
  stable meeting numbers `1` and `2`.
- Whole-recurring day/time changes are locked when the official timetable is
  published for student registration. A long-term room failure may create an
  audited room-only segment with the same day and slot.
- The accepted baseline soft weights are: lecturer preferences `10`, room
  waste `1`, large-hall use `25`, gaps `4`, scattered days `8`, excess
  consecutive sessions `6`, and evening/weekend avoidance `5`.
- The account policy is one role per account, exactly one Administrator, one
  Training Office account, and multiple Lecturer accounts. There is no public
  registration or password-reset workflow in the MVP.
- Dated CSV/XLSX exports use `DD-MM-YYYY`; CSV uses UTF-8 BOM and filenames use
  batch name, run/official code and timestamp.
- The performance target is 100-200 sections at the default population `80`
  and generation limit `200`, completing or preserving the best candidate
  within 10 minutes on the recorded reference machine. A publishable result
  must have zero hard violations.
- Because the university cannot disclose its source data, the supervisor has
  approved a fully synthetic scale-test batch with approximately 600 lecturers,
  3,000 course sections and 150 rooms. It must use the project-defined seven
  CSV files, contain no real personal data and remain clearly labelled as
  synthetic. This stress dataset does not replace the 100-200-section MVP
  performance acceptance target.

## 16. Confirmation Checklist

- [ ] At least one real sample dataset has been received and checked. No real
  dataset is available; the team-defined schema is the MVP fallback.
- [ ] Room-capacity rule has been confirmed in the final URS/SRS.
- [ ] Request - approval - apply-change workflow has been confirmed.
- [x] Deadline and room-only exception for the recurring schedule have been confirmed for the MVP.
- [x] Practical/integrated multi-meeting fields and week 16-18 make-up window have been confirmed for the MVP.
- [x] Initial soft constraints and weights have been confirmed for the MVP.
- [x] Dataset scale and run-time criteria have been confirmed for the MVP.
- [x] A synthetic university-scale stress dataset (about 600 lecturers, 3,000
  sections and 150 rooms) is approved because real university data cannot be
  disclosed.
- [x] Export file format has been confirmed for the MVP.
- [x] Three-role permission matrix and account-provisioning policy have been confirmed for the MVP.
- [x] Bulk Lecturer provisioning, unique one-time temporary passwords,
  mandatory first-login password change and Administrator-issued Lecturer
  password reset have been confirmed for the MVP.
- [ ] Lecturer calendar layout and supported week/session interactions have been confirmed.
- [ ] Demo and delivery requirements have been confirmed.
- [ ] Conclusions have been updated into URS 1.0 and SRS 1.0.

