# Software Requirements Specification

## 1. Document Information

| Field | Value |
| --- | --- |
| Project | Teaching Timetable Scheduling Application Using Genetic Algorithm |
| Document | Software Requirements Specification (SRS) |
| Source file | `D:\DoAn\DuAn\TaiLieu_SRS.docx` |
| Version | 0.4 draft |
| Created | 08/07/2026 |
| Updated | 23/08/2026 |
| Status | Draft; MVP business decisions confirmed by the project owner, final delivery/demo pending supervisor confirmation |

## 2. Purpose

This document specifies software requirements for a web application that supports teaching timetable generation using a Genetic Algorithm. It refines the user requirements into functional requirements, data requirements, constraints, acceptance criteria and test direction.

## 3. Scope

### 3.1 In Scope

- CSV import, preview, validation, mapping and normalization.
- Genetic Algorithm configuration and execution.
- Timetable views by lecturer, room and course section.
- Login, authorization and lecturer weekly personal timetable.
- Administrator account provisioning, role assignment and account activation/deactivation.
- Separate role-specific portals for Administrator, Training Department and Lecturer; no student or public account access.
- Lecturer requests to suspend, move one session or move a whole recurring schedule within the allowed period.
- Training Department approval/rejection of change requests.
- Conflict checking before applying changes.
- CSV/Excel export.
- Run history, request history and experiment metrics.

### 3.2 Out of Scope

- Student course registration.
- Tuition, grade or student profile management.
- Separate mobile application.
- Official integration with the university management system without a provided integration API.
- Automatic email/SMS notifications unless added to scope.
- Replacing unrelated training-management workflows.
- Guaranteeing a globally optimal timetable for all datasets.

## 4. Actors and Permissions

| Actor | Main permissions | Limits |
| --- | --- | --- |
| Administrator | Log in; create and manage approved user accounts; assign Administrator, Training Office or Lecturer roles; activate/deactivate access; view account/audit information. | The MVP allows exactly one protected Administrator account with one role; it does not upload data, run GA or edit official timetables. Cannot create student or public accounts. |
| Training Department / Manager | Log in; import data; configure and run GA; view all schedules; receive, check, approve or reject change requests; apply changes; export data; view run and request history. | May apply changes only after data is valid and hard constraints are checked. |
| Lecturer | Log in; view personal weekly timetable; view class details; submit suspend/move requests; track request status. | Cannot directly edit timetables, add classes, delete classes, reject classes, approve requests or edit another lecturer's timetable. |
| Supervisor / tester | Provide data, test functions and evaluate results. | May not be a regular operational account. |

## 5. Priority Levels

| Level | Meaning |
| --- | --- |
| Must | Required for minimum acceptance and project completion. |
| Should | Important, implemented when it does not block Must requirements. |
| Could | Optional improvement. |
| TBD | Needs additional decision or confirmation. |

## 6. Data Requirements

### 6.1 Course Sections

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `course_code` | String | Yes | Course code, not blank. |
| `course_name` | String | Yes | Course name. |
| `section_code` | String | Yes | Course-section code, unique within a semester/dataset. |
| `lecturer_code` | String | Yes | Must reference an existing lecturer. |
| `required_sessions` | Integer | Yes | Greater than 0. |
| `weekly_sessions` | Integer | Yes | Normally 1; may be 2 for an explicitly declared practice/integrated multi-meeting section. |
| `periods_per_session` | Integer | Yes | Period count of the first or only declared weekly meeting. |
| `second_session_periods` | Integer | Conditional | Required only when `weekly_sessions=2`; normally `2` for a `3+2` five-period load or `3` for a `3+3` six-period load. |
| `expected_students` | Integer | Yes | Greater than 0. |
| `initial_registration_limit` | Integer | Should | Initial registration limit, usually around 50 or 55. |
| `approved_max_students` | Integer | Should | Approved maximum after adjustment, possibly 60 or 65 depending on room/business rule. |
| `current_registered_students` | Integer | No | Current actual registered count when synchronized. |
| `scheduling_student_count` | Integer / computed | Yes | Use `approved_max_students`, otherwise `initial_registration_limit`, otherwise `expected_students`. |
| `course_type` | Enum | Yes | `THEORY`, `PRACTICE` or `INTEGRATED`. |
| `required_room_type` | Enum/String | Yes | Explicit room requirement; do not infer only from course type. |
| `weeks` | String / list | Should | Teaching week list or range. |
| `campus_code` | String | Could | Campus/building area if multiple campuses exist. |
| `notes` | String | No | Business notes. |

### 6.2 Rooms

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `room_code` | String | Yes | Unique room code. |
| `room_name` | String | Yes | Display name. |
| `capacity` | Integer | Yes | Greater than 0. |
| `room_type` | Enum | Yes | `THEORY_ROOM`, `COMPUTER_LAB`, `SPECIALIZED_LAB` or another documented compatible room type. |
| `campus_code` | String | Should | Campus/building area. |
| `available` | Boolean | Yes | Whether the room can be used in the semester. |
| `unavailable_slots` | List | No | Slots where the room cannot be used. |

### 6.3 Time Slots

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `slot_code` | String | Yes | Unique slot code. |
| `day_of_week` | Number / enum | Yes | Monday to Sunday. |
| `start_period` | Integer | Yes | Start period. |
| `end_period` | Integer | Yes | Must be greater than or equal to `start_period`. |
| `session_type` | Enum | Should | Morning, afternoon or evening. |
| `supports_course_types` | List/String | Yes | Course types supported by this configured slot. |
| `active` | Boolean | Yes | Whether the slot is usable for scheduling. |

### 6.4 Lecturers

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `lecturer_code` | String | Yes | Unique lecturer code. |
| `lecturer_name` | String | Yes | Lecturer full name. |
| `time_preferences` | List | No | Preferred or undesired teaching slots are treated as soft constraints. A slot becomes a hard restriction only when officially confirmed by the Training Department. |
| `preferred_slots` | List | No | Treated as soft constraints. |
| `max_days_per_week` | Integer | No | Desired maximum teaching days; hard/soft status needs confirmation. |
| `max_consecutive_sessions` | Integer | No | Desired maximum consecutive sessions. |

## 7. Data Validation Rules

| Code | Rule | Handling |
| --- | --- | --- |
| DV-01 | File must be readable CSV. | Reject file. |
| DV-02 | Required columns must not be missing. | Reject file and list missing columns. |
| DV-03 | Identifiers and required fields must not be blank. | Mark row error. |
| DV-04 | Numeric values must have valid type and be greater than 0 where required. | Mark row/column error. |
| DV-05 | Lecturer and room references must exist. | Reject invalid rows. |
| DV-06 | Course-section code must not duplicate within the same import batch. | Mark duplicate rows. |
| DV-07 | Course type and room type must be in allowed dictionaries. | Mark invalid value. |
| DV-08 | Time slots must be in the valid slot list. | Mark or remove according to user choice. |
| DV-09 | System must report row, column, value and reason. | Show validation report. |
| DV-10 | User must confirm before overwriting an existing import batch. | Require confirmation. |
| DV-11 | Room capacity must be greater than or equal to `scheduling_student_count`. | Mark room as unsuitable. |
| DV-12 | If real files use different column names, system must map to the standard model before saving. | Require mapping or reject import. |

## 8. Functional Requirements

### 8.1 Authentication and Authorization

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-AUTH-01 | System allows users to log in with a valid account. | Must | Correct account can access; incorrect account is rejected with a message. |
| FR-AUTH-02 | System identifies Administrator, Training Office and Lecturer roles. | Must | Each account only sees functions for its role. |
| FR-AUTH-03 | Administrators can create, update, activate/deactivate and assign roles to approved user accounts. | Must | Account changes are restricted to Administrators and are auditable. |
| FR-AUTH-04 | System rejects students, unprovisioned accounts and outside users; public self-registration is not available. | Must | Login is denied with a safe message and no protected data is exposed. |
| FR-AUTH-05 | Lecturers can only view personal schedules, submit requests for assigned classes and cannot directly edit timetables. | Must | API and UI reject unauthorized access or updates. |
| FR-AUTH-06 | Training Department can view, approve, reject and apply change requests after validation. | Must | Only the correct role can access approval features. |
| FR-AUTH-07 | System allows logout and session termination. | Must | Protected pages require login again after logout. |
| FR-AUTH-08 | Administrator can explicitly bulk-provision Lecturer accounts from a confirmed batch for selected lecturer codes or all lecturers. | Must | Operation is idempotent, reports created/skipped/conflicting accounts, binds each account to one stable `lecturer_code`, and does not run automatically on CSV import. |
| FR-AUTH-09 | Bulk provisioning generates a different cryptographically random temporary password for each new account and may write it once to a local ignored credentials file. | Must | Database stores only hashes; no shared default exists; passwords are not printed in ordinary logs or committed to Git. |
| FR-AUTH-10 | Accounts created or reset with a temporary password are marked `must_change_password` and cannot enter the normal portal until they replace it. | Must | Successful replacement clears the flag and invalidates other active sessions. |
| FR-AUTH-11 | Administrator can issue a new temporary password for a Lecturer who has lost access. | Must | Old password is never shown; new value is displayed once, existing sessions are revoked, `must_change_password` is restored and `PASSWORD_RESET_BY_ADMIN` is audited. |
| FR-AUTH-12 | Authenticated users can change their own password by supplying the current password. | Must | Password policy is enforced, sessions are rotated/revoked safely, and no public forgot-password endpoint or form is introduced. |

### 8.2 Data Import

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-DATA-01 | Manager can upload one complete seven-file CSV batch exported from Excel. | Must | All required files are recognized, validated together and shown as one batch. |
| FR-DATA-02 | System previews data before saving. | Must | Shows column headers and sample rows; user can cancel. |
| FR-DATA-03 | System validates structure, data types and references. | Must | Reports all found errors by row and column. |
| FR-DATA-04 | Manager can download import error report. | Should | Report contains row, column, value and reason. |
| FR-DATA-05 | System saves only import batches confirmed by the user. A later correction creates a new batch version and does not overwrite a batch used by an earlier GA run. | Must | No new data is saved when user cancels; previous runs remain reproducible. |
| FR-DATA-06 | System stores import batch code, type, time, importer and status. | Should | Import batch can be looked up later. |
| FR-DATA-07 | Manager can choose a confirmed dataset batch for a GA run. The built-in sample dataset is restricted to development and demonstration. | Must | Run is linked to the selected batch and data version. |
| FR-DATA-08 | Manager can delete or deactivate unused import batches by permission. | Could | Existing saved results are not broken. |

### 8.3 Genetic Algorithm

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-GA-01 | Manager can configure population size. | Must | Value is checked within the allowed range. |
| FR-GA-02 | Manager can configure number of generations. | Must | Valid value is stored with the run. |
| FR-GA-03 | Manager can configure crossover and mutation rates. | Must | Only values from 0 to 1 are accepted. |
| FR-GA-04 | Manager can configure soft-constraint weights. | Must | Weights are stored and reflected in fitness evaluation. |
| FR-GA-05 | System checks data readiness before running. | Must | Does not run when required data is missing; shows reason. |
| FR-GA-06 | System initializes and executes GA to create a timetable option. | Must | Creates a result or failure status with reason. |
| FR-GA-07 | System updates run status: pending, running, completed, failed or stopped. | Must | UI reflects current status accurately. |
| FR-GA-08 | System stores the best option found during the run. | Must | Best result is stored when stop condition is reached. |
| FR-GA-09 | Manager can set time limit or stop a run. | Should | System stops safely and keeps the best result if available. |
| FR-GA-10 | System records configuration, run time, fitness and violation counts by group. | Must | Metrics are viewable after run. |
| FR-GA-11 | System supports random seed for reproducible experiments. | Should | Same data, config and seed can reproduce equivalent result. |
| FR-GA-12 | Manager can re-run algorithm to create a new option. | Must | Creates a new run and does not overwrite old history unless confirmed. |

### 8.4 Timetable Views

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-VIEW-01 | Show timetable by lecturer. | Must | Shows course, section, date/week, slot/period and room. |
| FR-VIEW-02 | Show room usage schedule. | Must | User can select a room and view classes by time. |
| FR-VIEW-03 | Show timetable by course section. | Must | Shows all sessions of the section. |
| FR-VIEW-04 | Lecturer can view personal weekly timetable and switch weeks. | Must | Only the logged-in lecturer's schedule is shown. |
| FR-VIEW-05 | User can open session details. | Should | Full information and status are shown. |
| FR-VIEW-06 | System supports filtering by lecturer, room, section, date or week. | Should | Filtered results are correct and filters can be cleared. |
| FR-VIEW-07 | System shows soft-violation warnings for an option. | Should | Manager can see count and type of violations. |
| FR-VIEW-08 | Lecturer portal provides a personal weekly calendar with week navigation and session details. | Must | Only assigned sessions are shown; empty, loading and error states are handled. |

### 8.5 Change Requests and Make-up Sessions

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-REQ-01 | Lecturer can submit request to suspend one session, move one session or move a whole recurring schedule for an assigned course section. | Must | Only assigned classes can be selected. |
| FR-REQ-02 | Request must record type, section, affected session/timetable, reason and proposed option if any. | Must | Missing required fields are rejected. |
| FR-REQ-03 | Submitted request has Pending status and does not change official timetable. | Must | Timetable remains unchanged until approval. |
| FR-REQ-04 | Training Department can view details, approve or reject requests. | Must | Result is stored with handler, time and note. |
| FR-REQ-05 | Before approving a move, system checks lecturer, room, time slot, room type, capacity and teaching week conflicts. | Must | Hard-constraint violations are not applied and reasons are shown. |
| FR-REQ-06 | System updates suspension status or new timetable only after approval. | Must | Approved request creates traceable timetable/status data. |
| FR-REQ-07 | If rejected, timetable remains unchanged and lecturer sees reason. | Must | Status becomes Rejected; schedule data is unchanged. |
| FR-REQ-08 | Lecturer can track requests they submitted. | Must | Lecturer sees only their own requests. |
| FR-REQ-09 | Moving a whole recurring day/time schedule is allowed only before the official timetable is published for student registration. | Must | After publication, a whole-recurring day or slot change is rejected. |
| FR-REQ-10 | Lecturer cannot add, delete, reject classes or approve requests. | Must | UI does not provide action; API rejects operation. |
| FR-REQ-11 | System stores request/change history: requester, approver, time, old data, new data, reason and status. | Must | Full trace is available from request to applied schedule. |
| FR-REQ-12 | Lecturer can cancel a request while it is Pending. | Should | Request becomes Cancelled and cannot be approved. |
| FR-REQ-13 | A suspended regular occurrence counts as one missing required session. | Must | Missing-session count increases until an applicable make-up session is recorded. |
| FR-REQ-14 | Training Department can manually add a make-up session on a valid teaching date through academic week 18, including weeks 16-18 after a normal 15-week section. | Must | Week 18 is accepted; week 19 and later are rejected; all hard constraints are checked. |
| FR-REQ-15 | A make-up session should retain the affected missing occurrence when known. | Should | `original_missing_date` is visible in history and can be used to reconcile the missing count. |
| FR-REQ-16 | After publication, Training Department may create a long-term room-only segment for a facility failure while preserving the recurring day and slot. | Must | Reason and audit are stored; the replacement room passes type, capacity, availability and overlap validation. |

Implementation note (13/08/2026): the MVP workflow separates approval from
application. A valid request follows `PENDING -> APPROVED -> APPLIED`; a
pending request may instead become `REJECTED` or `CANCELLED`. Approval does not
change the official timetable. Application rechecks the current official
timetable and all hard constraints before saving the change and audit history
in one transaction.

The first implemented request slice covers suspending or moving one dated
occurrence. `MOVE_RECURRING_SCHEDULE` must use publication status as the lock:
before publication it may be processed after validation; after publication a
day/time change is unavailable. A room-only date-range segment remains allowed
for a long-term facility issue when it preserves the day and slot.

### 8.6 Export

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-EXP-01 | Manager can export timetable to CSV. | Must | File opens correctly, uses UTF-8 and contains required fields. |
| FR-EXP-02 | Manager can export timetable to Excel `.xlsx`. | Must | File opens correctly and matches the selected option. |
| FR-EXP-03 | Export can be scoped to full timetable, lecturer, room or course section. | Should | File contains only selected scope. |
| FR-EXP-04 | Export filename contains batch name, timestamp and option/run or official code. Dated export cells use `DD-MM-YYYY`; API dates remain ISO. | Should | Filename is traceable and dates are familiar to Vietnamese spreadsheet users. |

### 8.7 Run History and Audit

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-AUD-01 | System stores GA run list. | Must | Each run has a unique code, status and time. |
| FR-AUD-02 | Manager can view configuration and metrics of each run. | Must | Shows parameters, fitness, time, seed and violation counts. |
| FR-AUD-03 | Manager can compare at least two runs. | Could | Shows comparison table of key metrics. |
| FR-AUD-04 | System logs important technical and business errors. | Should | Logs contain timestamp, level and enough diagnostic information. |

### 8.8 User and Role Administration

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-ADMIN-01 | Administrator can list and search user accounts by name, username, role and status. | Must | Results are limited to approved account records. |
| FR-ADMIN-02 | Administrator can create an account and assign exactly one application role. | Must | Invalid roles and duplicate usernames are rejected. |
| FR-ADMIN-03 | Administrator can activate or deactivate an account without deleting audit history. | Must | Deactivated users cannot create a session. |
| FR-ADMIN-04 | Administrator actions are recorded with actor, time, target account, old value and new value where applicable. | Should | Audit record is available for review. |

## 9. Scheduling Constraints

### 9.1 Hard Constraints

| Code | Constraint | Handling |
| --- | --- | --- |
| HC-01 | A lecturer must not teach two classes at the same time. | Reject, repair or penalize so the option cannot be selected. |
| HC-02 | A room must not host two classes at the same time. | Reject, repair or penalize so the option cannot be selected. |
| HC-03 | Each course section must receive the required number of sessions. | Reject, repair or penalize so the option cannot be selected. |
| HC-04 | Each session must use a valid time slot. | Reject, repair or penalize so the option cannot be selected. |
| HC-05 | Room type must match course-section type. | Reject, repair or penalize so the option cannot be selected. |
| HC-06 | Room physical capacity must be greater than or equal to `scheduling_student_count`. | Reject, repair or penalize so the option cannot be selected. |
| HC-07 | Lecturer must not be scheduled into officially confirmed fixed restrictions. Lecturer self-declared preferences remain soft unless confirmed. | Reject, repair or penalize so the option cannot be selected. |
| HC-08 | Room must not be scheduled into unavailable slots. | Reject, repair or penalize so the option cannot be selected. |
| HC-09 | A session must have course section, lecturer, room and time slot. | Reject, repair or penalize so the option cannot be selected. |
| HC-10 | Regular sessions must be inside the section's normal date range. A make-up session may use a valid configured teaching date through academic week 18; academic week 19 and later are outside the current make-up window. | Reject the invalid regular or make-up session. |
| HC-11 | Each declared weekly meeting receives one base assignment. No minimum day gap is required; consecutive-day meetings are valid when all other hard constraints pass. | Reject missing/duplicate meeting assignments or other hard violations. |
| HC-12 | Change requests may be applied only after Training Department approval and must not create new hard-constraint violations. | Reject the change. |

### 9.2 Soft Constraints

| Code | Constraint | Evaluation |
| --- | --- | --- |
| SC-01 | Prefer lecturer desired time slots and avoid lecturer undesired time slots. | Count/magnitude of violations multiplied by configured weight. |
| SC-02 | Avoid too many consecutive sessions for a lecturer. | Count/magnitude of violations multiplied by configured weight. |
| SC-03 | Reduce gaps between sessions in the same day. | Count/magnitude of violations multiplied by configured weight. |
| SC-04 | Distribute teaching schedule reasonably across the week. | Count/magnitude of violations multiplied by configured weight. |
| SC-05 | Prefer weekday and daytime sessions through configurable project weights. Saturday, Sunday and evening slots remain valid; waive the matching default penalty when the lecturer explicitly prefers that day or slot. | Count/magnitude of avoidable assignments multiplied by configured weight. |
| SC-06 | Prefer room capacity close to class size to reduce waste. | Count/magnitude of violations multiplied by configured weight. |
| SC-07 | Avoid frequent campus changes for one lecturer when campus data exists. | Count/magnitude of violations multiplied by configured weight. |
| SC-08 | Prefer schedule stability for sessions of the same course section. | Count/magnitude of violations multiplied by configured weight. |
| SC-09 | Prefer fewer soft violations when all hard constraints pass. | Count/magnitude of violations multiplied by configured weight. |

## 10. Non-Functional Requirements

| Code | Group | Requirement | Level |
| --- | --- | --- | --- |
| NFR-PERF-01 | Performance | Normal lookup operations should respond within a target of no more than 3 seconds for initial test data, excluding large file upload time. | Should |
| NFR-PERF-02 | Performance | Weekly timetable display must use paging/filtering and avoid loading unnecessary full datasets. | Must |
| NFR-PERF-03 | Performance | With 20 lecturers and 100-200 course sections at default population 80 and generation limit 200, system should complete or save the best solution within 10 minutes on the recorded reference machine. | Should |
| NFR-SCAL-01 | Scalability | Design must allow testing with larger approved datasets, including synthetic university-scale batches when real source data cannot be disclosed. | Must |
| NFR-SCAL-02 | Scalability | GA module must be separated from UI and API layers so it can be optimized or run in a separate process. | Must |
| NFR-SCAL-03 | Scalability | Provide a reproducible synthetic stress dataset of approximately 600 lecturers, 3,000 course sections and 150 rooms because source university data cannot be disclosed. The batch must use the seven-file project schema, contain no real personal data and be labelled synthetic. | Must |
| NFR-SEC-01 | Security | Passwords must not be stored in plain text; use suitable hashing if login is implemented. | Must |
| NFR-SEC-02 | Security | All APIs must check permissions, not only hide frontend controls. | Must |
| NFR-SEC-03 | Security | Uploaded files must be checked for type, size and safe filename. | Must |
| NFR-SEC-04 | Security | There is no public self-registration or student/external-user login; only Administrator-provisioned active accounts may access the application. | Must |
| NFR-SEC-05 | Security | Temporary passwords must be unique, random, shown/exported only once, excluded from logs and version control, and replaced on first login. | Must |
| NFR-REL-01 | Reliability | Schedule changes must not be saved if hard-constraint checking fails. | Must |
| NFR-REL-02 | Reliability | Failure in one run must not corrupt input data or results from previous runs. | Must |
| NFR-REL-03 | Reliability | System should record failure status and diagnostic information. | Should |
| NFR-USA-01 | Usability | Interface uses Vietnamese, consistent terms and clear error messages. | Must |
| NFR-USA-02 | Usability | Important operations such as overwrite, delete or official-option selection should require confirmation. | Should |
| NFR-MNT-01 | Maintainability | Source code is modular and includes installation/configuration instructions. | Must |
| NFR-MNT-02 | Maintainability | Constraints and soft weights should be configured or centralized in a clear module. | Should |
| NFR-TST-01 | Testing | Unit tests exist for conflict checking, fitness function and important data handling. | Must |
| NFR-COMP-01 | Compatibility | Web application supports current Chrome and Edge versions on desktop. | Should |
| NFR-DATA-01 | Data | CSV uses UTF-8; Excel export uses `.xlsx`. | Must |
| NFR-DEP-01 | Deployment | System can run from installation guide; Docker Compose is recommended. | Should |

## 11. Acceptance Criteria

1. Valid CSV files can be uploaded, previewed, validated and confirmed before saving.
2. Invalid CSV files produce clear validation messages by row, column and reason.
3. GA cannot run when required data is missing.
4. GA can generate a timetable for a small dataset with zero hard-constraint violations.
5. Run status and key metrics are recorded.
6. Training Department can view timetable by lecturer, room and course section.
7. Lecturer can view only their personal weekly timetable.
8. Lecturer can submit a change request without directly changing the official timetable.
9. Training Department can approve or reject a change request after conflict checking.
10. A change that violates hard constraints is not saved.
11. Timetable can be exported to UTF-8 CSV and `.xlsx`.
12. Administrator can manage approved accounts and role assignments without exposing timetable operations to unauthorized roles.
13. Source code, sample data, installation guide and experiment results are available for handoff.

## 12. Test Strategy

- Unit tests for CSV validation, conflict checking, hard constraints, soft scoring and fitness function.
- Integration tests for import flow, GA run flow, timetable query flow, export flow and change-request workflow.
- Permission tests for administrator, lecturer-only and Training Department-only operations.
- UI tests or manual test scripts for the main MVP flows.
- UI tests or manual scripts for role-specific navigation, the lecturer weekly calendar and administrator account management.
- Performance experiments with small, medium and larger/supervisor-provided datasets.

## 13. Test Dataset Levels

| Level | Purpose |
| --- | --- |
| Small | Verify correctness and hard-constraint handling. |
| Medium | Tune GA parameters and observe performance. |
| Large / real | Evaluate scalability, processing time, violation counts, fitness and resource usage. |

## 14. Traceability Map

| Requirement group | Planned module | Use case / workflow | Test group |
| --- | --- | --- | --- |
| FR-AUTH | Authentication / Authorization | Login, three-role access, lecturer personal timetable, request handling | Security, integration, permission |
| FR-ADMIN | User and Role Administration | Provision accounts, assign roles, activate/deactivate users, audit account changes | Integration, permission, security |
| FR-DATA | Import Service, Validation Service | CSV import and validation | Unit, integration, system |
| FR-GA | GA Engine, Run Service | Configure, run and re-run GA | Unit, performance, system |
| FR-VIEW | Schedule Query, Frontend Calendar | Timetable views | Integration, UI |
| FR-REQ | Request Workflow, Approval Service, Conflict Checker | Submit, approve, reject and apply changes | Unit, integration, permission, workflow |
| FR-EXP | Export Service | CSV/Excel export | Integration, file validation |
| FR-AUD | Run History, Audit Log | View run history and metrics | Integration, system |
| NFR-PERF / NFR-SCAL | GA Engine, Database, API | Experiment and scale testing | Performance |
| NFR-SEC | Auth, API middleware, Upload | Protected operations and safe uploads | Security |

## 15. Business Decisions and Open Issues

### 15.1 Clarified Decisions in SRS Draft

- Room capacity is a physical limit.
- Capacity checking uses `scheduling_student_count`.
- `scheduling_student_count` prioritizes `approved_max_students`, then `initial_registration_limit`, then `expected_students`.
- Lecturers can submit requests but cannot directly change official timetables.
- Training Department approval is required before applying changes.
- Authorization must be enforced by backend APIs.
- Only Administrator-provisioned active accounts may log in; students and outside users are not application actors.
- The bootstrap/system Administrator account is protected: normal account management cannot edit its identity, role or active state.
- Each Lecturer account is provisioned separately and bound to exactly one `lecturer_code` from the latest confirmed CSV batch; lecturer APIs filter by that authenticated code. Importing a lecturer row does not silently create a password or account.
- The `lecturer_code` is the stable identity across semesters. When a later confirmed batch contains the same code, the existing account is reused; the Administrator does not create a second account for that lecturer.
- A confirmed batch with 600 lecturer rows does not require 600 login accounts
  for an ordinary GA or demo test. The Administrator may provision only a
  representative subset; the same idempotent operation can provision all
  lecturers when account-scale testing is explicitly required.
- Bulk provisioning generates unique random temporary passwords and writes
  plaintext values only once to an ignored local handoff file. Temporary
  accounts must change password before normal portal access.
- An Administrator may reset a Lecturer by issuing a new one-time temporary
  password. The old password is not recoverable; existing sessions are revoked
  and the reset is audited. Authenticated users may change their own password.
- The MVP implementation follows `FR-ADMIN-02`: each account has exactly one application role. An `ADMIN` account is separated from timetable operations and does not inherit `TRAINING_OFFICE` permissions.
- The confirmed MVP policy is exactly one role per account, one protected
  `ADMIN`, one `TRAINING_OFFICE`, and multiple `LECTURER` accounts. Multi-role,
  public registration and public/self-service forgotten-password recovery are
  outside this MVP. Administrator-issued Lecturer temporary-password reset is
  explicitly included.
- Lecturer portal uses a weekly calendar with week navigation; the exact visual design remains an implementation decision.
- The Training Department prepares the complete seven-file CSV batch in Excel, previews and validates it, then confirms it before it can be used by GA. Built-in sample data is only for development and demonstration.
- The accepted baseline soft weights are lecturer preferences `10`, room
  capacity waste `1`, large-room/small-class `25`, schedule gaps `4`, scattered
  days `8`, excess consecutive sessions `6`, and evening/weekend avoidance `5`.
  They remain configurable, are stored with every run, and lecturer-specific
  preferred days/slots waive the matching default avoidance.
- A suspended or missed regular occurrence creates one missing required session.
  Training Department may manually place a validated make-up session in
  academic week 16, 17 or 18 even when the regular section ends after week 15.
  Week 19 and later are outside the current make-up window.
- No real university CSV was provided. The project-defined seven-file schema
  and anonymized fixtures are the operational MVP contract, without claiming
  production-system compatibility.
- Most sections have one weekly meeting. An explicitly declared `PRACTICE` or
  `INTEGRATED` section may have two weekly meetings. A five-period load is
  normally `3+2`; a six-period load may be `3+3`. The meetings remain the same
  integrated/practice section and are not separate theory/practice entries.
  There is no minimum day gap. The seven-file schema uses `weekly_sessions`,
  `periods_per_session`, optional `second_session_periods`, and derived stable
  meeting numbers.
- Whole-recurring day/time changes lock when the official timetable is
  published for student registration. After publication, only an audited
  room-only segment may handle a long-term facility problem while retaining
  the same day and slot.
- Dated CSV/XLSX cells use `DD-MM-YYYY`; CSV uses UTF-8 BOM and the filename
  contains batch name, run/official code and timestamp.
- The run target is 100-200 sections, default population `80`, generation limit
  `200`, zero hard violations for publication, and completion or best-candidate
  preservation within 10 minutes on the recorded reference machine.

### 15.2 Open Issues / Risks

- A real production CSV is unavailable. Future production mapping remains a
  risk, while the team-defined seven-file schema is accepted for the MVP.
- The final delivery/demo package still requires supervisor confirmation.

