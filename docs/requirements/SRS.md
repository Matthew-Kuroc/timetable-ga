# Software Requirements Specification

## 1. Document Information

| Field | Value |
| --- | --- |
| Project | Teaching Timetable Scheduling Application Using Genetic Algorithm |
| Document | Software Requirements Specification (SRS) |
| Source file | `D:\DoAn\DuAn\TaiLieu_SRS.docx` |
| Version | 0.2 draft |
| Created | 08/07/2026 |
| Status | Draft, pending supervisor review and confirmation |

## 2. Purpose

This document specifies software requirements for a web application that supports teaching timetable generation using a Genetic Algorithm. It refines the user requirements into functional requirements, data requirements, constraints, acceptance criteria and test direction.

## 3. Scope

### 3.1 In Scope

- CSV import, preview, validation, mapping and normalization.
- Genetic Algorithm configuration and execution.
- Timetable views by lecturer, room and course section.
- Login, authorization and lecturer weekly personal timetable.
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
| `periods_per_session` | Integer | Yes | Usually 3 for theory classes. |
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
| FR-AUTH-02 | System identifies Training Office and lecturer roles for the MVP. | Must | Each account only sees functions for its role. |
| FR-AUTH-03 | Lecturers can only view personal schedules, submit requests for assigned classes and cannot directly edit timetables. | Must | API and UI reject unauthorized access or updates. |
| FR-AUTH-04 | Training Department can view, approve, reject and apply change requests after validation. | Must | Only the correct role can access approval features. |
| FR-AUTH-05 | System allows logout and session termination. | Must | Protected pages require login again after logout. |

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

### 8.5 Change Requests

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
| FR-REQ-09 | Moving a whole recurring schedule is allowed only before the configured business deadline, default before student registration. | Must | After the deadline, system rejects the request. |
| FR-REQ-10 | Lecturer cannot add, delete, reject classes or approve requests. | Must | UI does not provide action; API rejects operation. |
| FR-REQ-11 | System stores request/change history: requester, approver, time, old data, new data, reason and status. | Must | Full trace is available from request to applied schedule. |
| FR-REQ-12 | Lecturer can cancel a request while it is Pending. | Should | Request becomes Cancelled and cannot be approved. |

### 8.6 Export

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-EXP-01 | Manager can export timetable to CSV. | Must | File opens correctly, uses UTF-8 and contains required fields. |
| FR-EXP-02 | Manager can export timetable to Excel `.xlsx`. | Must | File opens correctly and matches the selected option. |
| FR-EXP-03 | Export can be scoped to full timetable, lecturer, room or course section. | Should | File contains only selected scope. |
| FR-EXP-04 | Export filename contains data type, timestamp and option/run code. | Should | Filename is traceable. |

### 8.7 Run History and Audit

| Code | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| FR-AUD-01 | System stores GA run list. | Must | Each run has a unique code, status and time. |
| FR-AUD-02 | Manager can view configuration and metrics of each run. | Must | Shows parameters, fitness, time, seed and violation counts. |
| FR-AUD-03 | Manager can compare at least two runs. | Could | Shows comparison table of key metrics. |
| FR-AUD-04 | System logs important technical and business errors. | Should | Logs contain timestamp, level and enough diagnostic information. |

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
| HC-10 | Sessions must be within allowed teaching weeks. | Reject, repair or penalize so the option cannot be selected. |
| HC-11 | If a course section has multiple sessions per week, confirmed spacing rules must be applied when available. | Reject, repair or penalize so the option cannot be selected. |
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
| NFR-PERF-03 | Performance | With 20 lecturers and 100-200 course sections, system should complete or save the best solution within configured time; initial target is 10 minutes on reference machine. | Should |
| NFR-SCAL-01 | Scalability | Design must allow testing with larger and supervisor-provided real datasets. | Must |
| NFR-SCAL-02 | Scalability | GA module must be separated from UI and API layers so it can be optimized or run in a separate process. | Must |
| NFR-SEC-01 | Security | Passwords must not be stored in plain text; use suitable hashing if login is implemented. | Must |
| NFR-SEC-02 | Security | All APIs must check permissions, not only hide frontend controls. | Must |
| NFR-SEC-03 | Security | Uploaded files must be checked for type, size and safe filename. | Must |
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
12. Source code, sample data, installation guide and experiment results are available for handoff.

## 12. Test Strategy

- Unit tests for CSV validation, conflict checking, hard constraints, soft scoring and fitness function.
- Integration tests for import flow, GA run flow, timetable query flow, export flow and change-request workflow.
- Permission tests for lecturer-only and manager-only operations.
- UI tests or manual test scripts for the main MVP flows.
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
| FR-AUTH | Authentication / Authorization | Login, role-based access, lecturer personal timetable, request handling | Security, integration |
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
- The Training Department prepares the complete seven-file CSV batch in Excel, previews and validates it, then confirms it before it can be used by GA. Built-in sample data is only for development and demonstration.
- A default soft policy may discourage evening, Saturday and Sunday assignments. These assignments remain valid, and lecturer-specific preferred days or slots override the matching default penalty.

### 15.2 Open Issues / Risks

- Real production CSV structures still need confirmation.
- Practical-class rules may require additional room/time constraints.
- Rules for classes with multiple sessions per week may need supervisor confirmation.
- Deadline for moving a whole recurring schedule must be finalized.
- Make-up class rules after suspension need confirmation.
- Initial soft-constraint weights need confirmation.
- Run-time targets depend on actual machine and dataset scale.

