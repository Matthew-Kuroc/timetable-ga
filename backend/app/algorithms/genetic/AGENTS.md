# Algorithm Module Agent Instructions

## 1. Scope

This file applies to all files inside:

`backend/app/algorithms/`

The repository-level `AGENTS.md` and `backend/AGENTS.md` also apply.

Subdirectories may contain more specific instructions. For example:

`backend/app/algorithms/genetic/AGENTS.md`

When instructions conflict, the closest `AGENTS.md` to the modified file takes
precedence.

---

## 2. Purpose

The `algorithms` package contains computational logic used to generate,
validate, evaluate, compare, or improve teaching timetable solutions.

Algorithm modules must remain independent from:

- HTTP controllers.
- API route handlers.
- Authentication.
- Authorization.
- ORM sessions.
- Database transactions.
- CSV file parsing.
- Frontend components.
- Framework-specific request or response objects.

Algorithms should receive validated and normalized domain data and return
explicit typed results.

---

## 3. Current Project Model

The application generates teaching timetables before students register for
course sections.

The approved scheduling model is:

- Each course section has exactly one primary lecturer.
- One lecturer may teach multiple course sections.
- One lecturer may teach multiple sections of the same course.
- One lecturer may teach different courses in the same semester.
- Each course section has one regular meeting per week.
- Practice classes are not split into student groups.
- One course section does not have multiple primary lecturers.
- Teaching assignments are determined before timetable generation.
- Algorithms do not assign lecturers to courses.

The scheduling algorithm selects:

- Teaching day.
- Valid time slot.
- Room.

The algorithm must not change:

- Course-section identity.
- Course identity.
- Primary lecturer.
- Required session duration.
- Required room type.
- Scheduling student count.

---

## 4. Supported Course Types

Supported course-section types are:

- `THEORY`
- `PRACTICE`
- `INTEGRATED`

### Theory

Theory classes normally use one three-period session.

Configured theory slots may include:

- Periods 1–3.
- Periods 4–6.
- Periods 7–9.
- Periods 10–12.
- Periods 13–15.

### Practice

Practice classes use one five-period or six-period session.

Current valid slots include:

- Periods 1–5.
- Periods 1–6.
- Periods 2–6.

### Integrated

An integrated course section:

- Combines theory and practice in one class.
- Uses one five-period or six-period session.
- Has one primary lecturer.
- Is processed using practice-length time-slot rules.
- May require a laboratory, computer room, specialized room, or normal theory
  room.

Do not infer room requirements only from the course type.

Use the explicit room requirement from normalized course-section data.

---

## 5. Valid Teaching Days and Time Slots

Monday through Sunday are valid teaching days.

Saturday, Sunday, and evening slots are valid teaching times. The project may
apply configurable soft avoidance weights to them when no lecturer-specific
preference applies.

An explicit lecturer preferred day or slot waives the matching default
avoidance weight. These assignments must never become hard-constraint
violations solely because of their time.

Algorithms must select only from configured valid time slots.

Do not create arbitrary period ranges such as:

- Periods 3–9.
- Periods 4–10.
- Periods 5–8.

A session must remain inside one valid teaching block.

Morning and afternoon teaching blocks must remain separated.

Overlap checks must compare actual period ranges rather than only comparing
time-slot codes.

Two ranges overlap when:

    start_a <= end_b
    and
    start_b <= end_a

For example, periods 1–5 overlap periods 2–6 even though their slot codes are
different.

---

## 6. Algorithm Architecture

Keep algorithm responsibilities separated.

Recommended concepts include:

- Input validation.
- Domain preprocessing.
- Feasible-domain generation.
- Timetable candidate representation.
- Hard-constraint validation.
- Soft-constraint evaluation.
- Search or optimization strategy.
- Repair logic.
- Result comparison.
- Diagnostic reporting.
- Progress reporting.

Do not create one large function that:

- Reads files.
- Queries the database.
- Runs the algorithm.
- Saves results.
- Formats API responses.

A preferred flow is:

    validated domain data
            ↓
    algorithm input adapter
            ↓
    preprocessing
            ↓
    algorithm execution
            ↓
    typed algorithm result
            ↓
    application service persists or returns result

---

## 7. Input Contracts

Algorithm modules must receive normalized domain objects.

Do not accept raw CSV rows inside core algorithm functions.

A general scheduling input may contain:

- Course sections.
- Teaching assignments.
- Lecturers.
- Lecturer preferences.
- Confirmed lecturer restrictions.
- Rooms.
- Room availability.
- Valid time slots.
- Academic-term information.
- Algorithm configuration.

Use explicit types or dataclasses.

Example concept:

    AlgorithmInput(
        course_sections=...,
        lecturers=...,
        rooms=...,
        time_slots=...,
        lecturer_preferences=...,
        lecturer_restrictions=...,
        room_unavailability=...,
        configuration=...,
    )

Do not make algorithm code depend on:

- CSV column names.
- Vietnamese display labels.
- ORM entities with lazy-loading behavior.
- Database identifiers that have not been validated.
- HTTP request schemas.

Convert application-layer data into stable algorithm-domain objects before
execution.

---

## 8. Output Contracts

Algorithm output must be explicit and explainable.

A result should include, when relevant:

- Execution status.
- Best timetable candidate.
- Hard-constraint violation count.
- Hard-constraint violation details.
- Soft-constraint cost.
- Soft-cost breakdown.
- Execution time.
- Number of iterations or generations.
- Stop reason.
- Random seed.
- Progress or history data.
- Diagnostics.

Do not return only one unexplained numeric fitness value.

Example concept:

    AlgorithmResult(
        status="COMPLETED",
        best_candidate=...,
        hard_violation_count=0,
        soft_cost=125.0,
        soft_breakdown={
            "lecturer_preferences": 25.0,
            "room_waste": 60.0,
            "schedule_gaps": 40.0,
        },
        execution_time_seconds=12.4,
        stop_reason="MAX_GENERATIONS",
        diagnostics=[],
    )

Application services are responsible for converting algorithm results into API
responses or database records.

---

## 9. Hard Constraints

Hard constraints determine whether a timetable is valid.

At minimum, shared scheduling validation must cover:

- A lecturer must not teach overlapping classes.
- A room must not host overlapping classes.
- Every course section must receive its required base assignment.
- The selected time slot must be configured and active.
- The time slot must support the course type and session duration.
- The room type must satisfy the course-section requirement.
- Room capacity must be sufficient.
- The room must be available.
- Confirmed mandatory lecturer restrictions must not be violated.
- Required assignment information must not be missing.
- A manual schedule change must not create a new hard conflict.
- Contradictory schedule segments must not apply to the same occurrence.

Do not silently accept a hard-constraint violation.

Do not convert a hard constraint into a soft constraint merely to obtain a
result.

Hard-constraint diagnostics should include:

- Constraint code.
- Course-section code.
- Lecturer code, when relevant.
- Room code, when relevant.
- Day and time slot.
- Human-readable reason.

---

## 10. Soft Constraints

Soft constraints measure timetable quality but do not make a timetable
invalid.

Supported soft preferences may include:

- Lecturer preferred teaching days.
- Lecturer preferred time slots.
- Lecturer undesired days.
- Lecturer undesired time slots.
- Reducing long gaps between sessions.
- Reducing unnecessarily scattered teaching days.
- Preferring compact lecturer schedules.
- Balancing teaching distribution.
- Reducing room-capacity waste.
- Preserving large rooms for large classes when standard rooms are available.
- Maintaining stable regular schedules.

Do not automatically penalize consecutive valid sessions or movement between
university buildings. Default evening/weekend avoidance must be configurable
and must respect the corresponding lecturer preference.

Soft-constraint weights must be configurable.

Each soft-constraint evaluator should be independently testable.

---

## 11. Room Rules

Every room has its own:

- Room code.
- Room type.
- Capacity.
- Availability status.
- Optional unavailable dates or time slots.

A room is locally compatible with a course section when:

- Its type satisfies the required room type.
- Its capacity is sufficient.
- It is active.
- It is available for the relevant time.

Room capacity is a hard constraint:

    room.capacity >= section.scheduling_student_count

The normalized scheduling student count should already be determined before
entering the algorithm module.

The business priority is:

1. Approved maximum student count.
2. Initial registration limit.
3. Expected student count.

Algorithms should normally receive the final field:

`scheduling_student_count`

Do not repeatedly recalculate this business rule in separate algorithms.

---

## 12. Large Rooms

Some standard rooms contain approximately 60 students.

Some large halls may contain approximately 130 students.

Large halls:

- Are not restricted to general-education courses.
- May be used by any compatible course section.
- May be used when standard rooms are unavailable.
- May be selected manually by the Training Office.

Using a large hall for a small class remains valid.

It may receive a configurable soft penalty.

Example measurement:

    unused_capacity = room.capacity - scheduling_student_count

A room that is too small is a hard violation.

A room that is much larger than necessary is only a soft-quality concern.

Do not make the large-room penalty so strong that the algorithm refuses to use
an otherwise valid available room.

---

## 13. Lecturer Restrictions and Preferences

Do not assume that every lecturer preference is an officially confirmed hard restriction.

Before course registration, unexpected future absences are generally unknown.

A lecturer condition is a hard restriction only when the input explicitly
marks it as:

- Confirmed.
- Fixed.
- Mandatory.

Other lecturer preferences should remain soft.

Examples of soft data:

- Preferred day.
- Preferred time slot.
- Undesired day.
- Undesired time slot.
- Preference for fewer teaching days.
- Preference for consecutive sessions.
- Preference for fewer timetable gaps.

When an input file contains a field such as `mandatory`, interpret it
explicitly.

Do not treat every row in `lecturer_time_preferences.csv` as hard without
checking the row's mandatory status.

---

## 14. Academic Calendar

The main scheduling algorithm creates a base weekly timetable.

A separate calendar-expansion service may convert base schedules into dated
session occurrences.

The academic calendar may contain:

- Semester start date.
- Semester end date.
- Academic week number.
- Teaching dates.
- Holidays.
- Non-teaching dates.

When a regular occurrence falls on a holiday:

- Do not create a normal dated session.
- Do not automatically move the session.
- Do not automatically mark it as suspended.
- Record that the course section may require a makeup session.

Manual makeup-session scheduling occurs outside the core optimization
algorithm.

Do not put holiday movement logic inside generic selection, crossover,
mutation, or scoring functions.

---

## 15. Schedule Segments

A course section may use different rooms or schedules during different date
ranges.

For example:

    Semester start–15/10:
    Monday, periods 1–3, room A303

    16/10–semester end:
    Monday, periods 1–3, room F201

For the MVP:

- The optimization algorithm creates one base weekly assignment.
- The Training Office may create date-range segments manually afterward.
- Algorithms do not need to generate multiple room segments automatically.

Shared validation utilities may be reused to validate:

- One-session edits.
- Date-range edits.
- Changes from one date to the end of the semester.
- Entire-course changes.

Segment persistence and request approval belong to application services, not
algorithm modules.

---

## 16. Pure Functions and Side Effects

Prefer pure functions for:

- Period-overlap checking.
- Room compatibility.
- Capacity checking.
- Lecturer-conflict detection.
- Room-conflict detection.
- Soft-cost calculation.
- Candidate comparison.
- Feasible-domain filtering.

Pure functions should:

- Produce the same output for the same input.
- Avoid modifying their arguments.
- Avoid database or network access.
- Avoid global mutable state.
- Be easy to test independently.

Keep side effects at the application boundary.

Algorithm functions must not:

- Commit database transactions.
- Write uploaded files.
- Send emails.
- Read browser sessions.
- Modify authentication state.
- Print large debug output.

---

## 17. Shared Constraint Utilities

Constraint logic used by multiple algorithms should be centralized.

Examples:

- `period_ranges_overlap`
- `lecturer_has_conflict`
- `room_has_conflict`
- `room_type_is_compatible`
- `room_capacity_is_sufficient`
- `time_slot_is_compatible`
- `mandatory_restriction_is_satisfied`

Do not maintain separate inconsistent versions of overlap logic in:

- Genetic Algorithm evaluation.
- Manual schedule validation.
- Schedule-segment validation.
- Request approval.

Where practical, reuse one domain-level validation service.

Algorithm-specific scoring may wrap shared validation but must not redefine the
business rule differently.

---

## 18. Determinism and Randomness

Algorithms using randomness must accept an injected or locally controlled
random generator.

Do not use uncontrolled global randomness across many functions.

Record the random seed with each run.

Fixed input, fixed configuration, fixed seed, and fixed code should produce
reproducible or meaningfully equivalent results.

Tests involving randomness must use fixed seeds.

Do not depend on execution order of unordered collections for reproducibility.

Use stable sorting or stable identifiers where necessary.

---

## 19. Configuration

Algorithm configuration must be explicit and validated.

Examples include:

- Population size.
- Number of generations.
- Crossover rate.
- Mutation rate.
- Time limit.
- Random seed.
- Stagnation limit.
- Repair-attempt limit.
- Soft-constraint weights.

Reject invalid configuration before execution.

Examples:

- Population size less than one.
- Negative generation count.
- Mutation rate outside 0–1.
- Crossover rate outside 0–1.
- Negative constraint weight.
- Empty required input.

Do not hide configuration constants throughout implementation files.

Use a typed configuration object.

---

## 20. Failure Handling

Expected algorithm failures must return actionable information.

Examples:

- No course sections were provided.
- No valid time slot exists for a section.
- No room satisfies the required type.
- No room has enough capacity.
- A lecturer reference is missing.
- A room reference is missing.
- Configuration is invalid.
- A feasible timetable was not found within the execution limit.

Do not return only:

    Algorithm failed.

A useful diagnostic should identify:

- The affected entity.
- The violated condition.
- Whether the problem is input data, configuration, or search failure.
- A possible corrective action.

Unexpected technical exceptions may be logged by the application layer.

Do not catch broad exceptions and silently return an empty timetable.

---

## 21. Performance

The initial target data is approximately:

- 20 lecturers.
- 100–200 course sections.
- About one base assignment per course section.
- Approximately 1,500–3,000 dated occurrences after calendar expansion.

Prepare useful indexes before repeated evaluation.

Examples:

- Course sections by lecturer.
- Assignments by lecturer and day.
- Assignments by room and day.
- Compatible rooms by room type and capacity.
- Compatible slots by course type and duration.
- Preferences by lecturer.

Avoid repeatedly scanning all rooms, lecturers, and assignments for every small
operation when an index can be reused safely.

Measure performance before introducing complex caching.

Correctness and explainability take priority over premature micro-optimization.

---

## 22. Progress Reporting

Long-running algorithms may expose structured progress information.

Possible progress fields include:

- Current iteration or generation.
- Best hard-violation count.
- Best soft cost.
- Average cost.
- Elapsed execution time.
- Best candidate identifier.
- Current status.

Do not print progress directly from core functions.

Use:

- Callbacks.
- Events.
- Progress-reporting interfaces.
- Returned history objects.

Do not report a fake percentage when meaningful progress cannot be calculated.

---

## 23. Testing Requirements

Every algorithm module must include tests appropriate to its behavior.

Shared algorithm and constraint tests should cover:

### Time conflicts

- Exact time-slot overlap.
- Partial period overlap.
- Periods 1–5 versus periods 2–6.
- Non-overlapping consecutive sessions.
- Weekend schedules.

### Lecturer rules

- One lecturer teaching multiple non-overlapping classes.
- One lecturer teaching multiple courses.
- Consecutive sessions remaining valid.
- Overlapping sessions being rejected.
- Mandatory restrictions being hard.
- Ordinary preferences remaining soft.

### Room rules

- Room-type compatibility.
- Incompatible room type.
- Sufficient capacity.
- Insufficient capacity.
- Room overlap.
- Standard-room preference.
- Large-room soft penalty.
- Large room remaining valid when required.

### Course types

- Theory with a three-period slot.
- Practice with a five-period slot.
- Practice with a six-period slot.
- Integrated class with a five-period slot.
- Integrated class with a six-period slot.
- Invalid slot and course-type combination.

### Algorithm behavior

- Valid input.
- Empty input.
- No feasible assignment.
- Invalid configuration.
- Fixed-seed reproducibility.
- Safe cancellation.
- Detailed diagnostics.
- A valid result ranking above an invalid result.

Use small datasets whose expected results can be verified manually.

---

## 24. Out-of-Scope Responsibilities

Algorithm modules must not implement:

- Student accounts.
- Student course registration.
- Student individual timetables.
- Student-availability matching.
- Automatic lecturer-to-course assignment.
- Lecturer qualification decisions.
- Practical-class student-group splitting.
- Multiple primary lecturers for one course section.
- Automatic substitute-lecturer assignment.
- Automatic makeup-date selection.
- Automatic schedule segmentation by date range.
- Automatic holiday-session movement.
- Email, SMS, or push notifications.
- Tuition or grade processing.
- Guaranteed globally optimal scheduling.
- Full production integration with the university system.

When a new algorithm requirement expands this scope, update the URS and SRS
before implementation.

---

## 25. Code Quality

- Use explicit type annotations.
- Prefer dataclasses or typed domain objects.
- Keep public interfaces small and clear.
- Keep evaluation functions independent and testable.
- Avoid mutable global state.
- Avoid deeply nested untyped dictionaries.
- Avoid hidden business-rule constants.
- Use stable constraint identifiers.
- Document non-obvious algorithm decisions.
- Remove debug prints before committing.
- Do not suppress type-checking errors without explanation.
- Do not duplicate validation rules.
- Do not import framework-specific modules into core algorithm code.

Prefer readable and explainable implementations over clever but opaque code.

---

## 26. Change Discipline

When adding or changing an algorithm rule:

1. Review the latest URS and SRS.
2. Confirm whether the rule is hard or soft.
3. Update domain types when required.
4. Update preprocessing and feasible-domain logic.
5. Update validation or scoring.
6. Update diagnostic messages.
7. Update sample CSV files when affected.
8. Add or update tests.
9. Update algorithm documentation.
10. Check whether old experiment results remain comparable.

Do not change the meaning of an existing constraint code without documenting
the change.

Do not change the interpretation of an algorithm result silently.

---

## 27. Definition of Done

An algorithm change is complete when:

- It follows the latest URS and SRS.
- It receives normalized typed input.
- It returns a typed explainable result.
- It remains independent of HTTP, ORM, and CSV parsing.
- It preserves fixed teaching assignments.
- It uses only configured valid time slots.
- It correctly detects partial period overlap.
- It correctly enforces room type and capacity.
- It treats Saturday and Sunday as valid teaching days.
- It distinguishes hard restrictions from soft preferences.
- It provides useful diagnostics.
- Random behavior is reproducible with a fixed seed.
- Relevant tests pass.
- No hard constraint is silently relaxed.
- Formatting, linting, and type checking pass.
