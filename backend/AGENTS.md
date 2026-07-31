# Genetic Algorithm Agent Instructions

## 1. Scope

This file applies to all files inside:

`backend/app/algorithms/genetic/`

The repository-level `AGENTS.md` and `backend/AGENTS.md` also apply.

When instructions conflict, this file takes precedence for the Genetic
Algorithm module.

This module is responsible only for generating and evaluating timetable
candidates. It must remain independent from:

- HTTP frameworks.
- API controllers.
- Database sessions.
- Authentication.
- Frontend code.
- File-upload handling.
- ORM models.

Use plain domain objects, typed data structures, and explicit input/output
contracts.

---

## 2. Algorithm Responsibility

The Genetic Algorithm receives validated and normalized timetable data.

It determines:

- Teaching day.
- Valid time slot.
- Room.

It does not determine:

- Which lecturer teaches a course section.
- Which course sections are opened.
- Student course registration.
- Student availability.
- Lecturer payroll or teaching workload assignment.
- Makeup dates based on student timetables.
- Whether a lecturer is qualified to teach a course.

Teaching assignments are fixed before the algorithm runs.

---

## 3. Approved Teaching-Assignment Model

The following rules are fixed:

- Each course section has exactly one primary lecturer.
- A lecturer may teach multiple course sections.
- A lecturer may teach multiple sections of the same course.
- A lecturer may teach different courses in the same semester.
- A lecturer may teach consecutive valid sessions.
- A lecturer must not teach overlapping sessions.
- A course section is not assigned to multiple primary lecturers.
- Practice classes are not split into student groups.
- The GA must not replace the assigned lecturer.

Do not interpret “one lecturer per course section” as “one course section per
lecturer.”

---

## 4. Weekly Schedule Model

Each course section has one regular meeting per week.

Examples:

- One theory class every Monday, periods 1–3.
- One practice class every Wednesday, periods 1–6.
- One integrated class every Saturday, periods 2–6.

A course section may produce approximately 15 dated occurrences during a
semester.

For the MVP:

- One gene represents one course section's base weekly assignment.
- The chromosome contains approximately one gene per course section.
- Do not create one independent gene for every dated occurrence.

Example gene concept:

    Gene(
        section_code="AI-01",
        lecturer_code="GV001",
        day_of_week=2,
        slot_code="LT_01_03",
        room_code="A301",
    )

The following values are fixed input data:

- `section_code`
- `lecturer_code`
- `course_type`
- `required_room_type`
- `periods_per_session`
- `scheduling_student_count`

The following values are selected by the GA:

- `day_of_week`
- `slot_code`
- `room_code`

Do not mutate fixed teaching-assignment fields.

---

## 5. Course Types

Supported course types are:

- `THEORY`
- `PRACTICE`
- `INTEGRATED`

### Theory

Theory classes normally contain three periods per session.

Possible configured theory slots include:

- Periods 1–3.
- Periods 4–6.
- Periods 7–9.
- Periods 10–12.
- Periods 13–15.

### Practice

Practice classes contain five or six periods.

Current valid practice slots include:

- Periods 1–5.
- Periods 1–6.
- Periods 2–6.

### Integrated

An integrated course section:

- Combines theory and practice in one session.
- Is represented as one course section.
- Has one primary lecturer.
- Uses five or six periods.
- Uses the same slot-length rules as practice classes.
- May require a laboratory or a normal theory room.

Do not infer the required room type only from `course_type`.

Use the explicit `required_room_type` supplied for the course section.

---

## 6. Valid Time Slots

The GA must select only from validated configured time slots.

Do not generate arbitrary values for:

- Start period.
- End period.
- Session duration.

Do not create invalid ranges such as:

- Periods 3–9.
- Periods 4–10.
- Periods 5–8.

A session must remain inside one valid teaching block.

Morning and afternoon sessions must remain separated.

Time-slot compatibility should be precomputed before population initialization.

Example compatibility:

    compatible_slots[section_code] = [
        slot for slot in time_slots
        if slot.supports(course_type, periods_per_session)
    ]

Fail input validation before running the GA when a section has no compatible
time slot.

---

## 7. Teaching Days

Monday through Sunday are valid teaching days.

Saturday, Sunday, and evening slots remain valid teaching times. A configurable
project-wide soft weight may discourage their use when no lecturer-specific
preference applies.

This default avoidance reflects the usual availability of lecturers; it is not
a hard constraint and must never make an otherwise feasible timetable invalid.

A lecturer may:

- Prefer weekends.
- Prefer weekdays.
- Have no day preference.
- Mark a day as undesirable.

If a lecturer explicitly prefers a day or slot, do not apply the corresponding
default avoidance penalty to that lecturer.

Keep these weights in GA configuration and store them with every run so the
result can be reproduced and explained.

---

## 8. Lecturer Preferences

Lecturer preferences are soft constraints unless explicitly marked as confirmed
fixed restrictions.

Supported preference concepts may include:

- Preferred days.
- Preferred time slots.
- Undesired days.
- Undesired time slots.
- Preference for compact teaching days.
- Preference for fewer long gaps.
- Preference for consecutive sessions.
- Preferred number of teaching days.

Unexpected future absences are not known during timetable generation.

Do not treat ordinary preference data as a hard unavailable schedule.

A lecturer restriction is hard only when input data explicitly marks it as:

- Confirmed.
- Fixed.
- Mandatory.

The sample field `mandatory` must be interpreted explicitly.

Do not convert every entry in `lecturer_time_preferences.csv` into a hard
constraint without checking that field.

---

## 9. Room Compatibility

A room assignment is valid only when:

- The room is available.
- The room is not used by another class at the same time.
- The room type satisfies the course-section requirement.
- Room capacity is greater than or equal to the scheduling student count.
- The room is active during the required period.

The scheduling student count should be provided by normalized input data.

Its business priority is:

1. Approved maximum student count.
2. Initial registration limit.
3. Expected student count.

Do not duplicate this business calculation in multiple GA functions.

Prefer receiving one finalized field:

`scheduling_student_count`

---

## 10. Room Capacity

Room capacity is a hard constraint.

Invalid assignment:

    room.capacity < section.scheduling_student_count

Valid assignment:

    room.capacity >= section.scheduling_student_count

Do not allow an infeasible room merely by applying a small soft penalty.

A room that is too small makes the gene or chromosome invalid.

The GA may either:

- Prevent the assignment during initialization.
- Repair the assignment.
- Apply a prohibitive hard penalty.
- Reject the individual.

Prefer preventing known impossible assignments before population generation.

---

## 11. Large Rooms

Some standard rooms contain approximately 60 students.

Some large halls may contain approximately 130 students.

Large halls:

- Are not restricted to general-education courses.
- May contain any compatible course section.
- May be used when standard rooms are unavailable.
- May later be selected manually by the Training Office.

Using a large hall for a small class is valid but may receive a soft penalty.

Example:

    unused_capacity = room.capacity - scheduling_student_count

Possible soft scoring:

- Small unused capacity: low or no penalty.
- Very large unused capacity: higher penalty.
- Negative unused capacity: hard violation.

Do not make a large-room penalty so high that the algorithm prefers an
infeasible timetable or fails to use an available room when necessary.

Large-room preference weights must be configurable.

---

## 12. Room and Lecturer Overlap

Overlap detection must use actual period ranges.

Do not compare only `slot_code`.

Example:

- Class A uses periods 1–5.
- Class B uses periods 2–6.

These classes overlap even though the slot codes differ.

Two period ranges overlap when:

    start_a <= end_b
    and
    start_b <= end_a

A lecturer conflict occurs when:

- The lecturer is the same.
- The day is the same.
- The period ranges overlap.

A room conflict occurs when:

- The room is the same.
- The day is the same.
- The period ranges overlap.

Use shared overlap utilities.

Do not maintain separate inconsistent overlap logic for lecturers and rooms.

---

## 13. Academic Calendar

The GA generates a base weekly timetable.

The academic calendar is used afterward to create dated occurrences.

The calendar may contain:

- Semester start date.
- Semester end date.
- Academic week number.
- Teaching days.
- Holidays.
- Non-teaching dates.

When a regular occurrence falls on a holiday:

- Do not create a normal session occurrence.
- Do not automatically move it.
- Do not mark it as suspended by the GA.
- Record that the course section may be missing a required session.

The Training Office may add a makeup session manually later.

Holiday expansion belongs in a schedule-expansion or calendar service, not in
selection, crossover, mutation, or fitness logic.

The GA should optimize the regular base timetable, not automatically solve all
makeup sessions.

---

## 14. Schedule Segments

A course section may use different rooms during different date ranges.

Example:

    Semester start–15/10:
    Monday, periods 1–3, room A303

    16/10–semester end:
    Monday, periods 1–3, room F201

For the MVP:

- The GA creates one base schedule for the whole course section.
- The Training Office may manually create multiple schedule segments afterward.
- The GA does not need to generate date-range room changes automatically.

Do not add date-range segmentation into chromosome design unless the URS and
SRS are formally changed.

Manual segment validation may reuse GA constraint utilities, but segment
persistence does not belong in the GA engine.

---

## 15. Hard Constraints

Hard constraints determine timetable validity.

At minimum, enforce:

- `HC-01`: A lecturer must not teach overlapping classes.
- `HC-02`: A room must not host overlapping classes.
- `HC-03`: Each course section must receive one base weekly assignment.
- `HC-04`: The selected time slot must be valid.
- `HC-05`: The slot must support the course type and session duration.
- `HC-06`: The room type must satisfy the course-section requirement.
- `HC-07`: Room capacity must satisfy the scheduling student count.
- `HC-08`: The room must be available.
- `HC-09`: A confirmed mandatory lecturer restriction must not be violated.
- `HC-10`: Required gene fields must not be missing.

A timetable candidate with any hard violation is not considered valid.

Do not silently convert a hard constraint into a soft constraint to obtain a
result.

Return hard-violation details grouped by:

- Constraint code.
- Lecturer.
- Room.
- Course section.
- Day and time slot.
- Human-readable reason.

---

## 16. Soft Constraints

Soft constraints measure timetable quality.

Possible soft constraints include:

- Lecturer preferred day.
- Lecturer preferred time slot.
- Lecturer undesired day.
- Lecturer undesired time slot.
- Long gaps between sessions.
- Excessively scattered teaching days.
- Excessive consecutive teaching sessions, when configured.
- Room-capacity waste.
- Use of large halls for small classes.
- Uneven teaching distribution.
- Lack of schedule compactness.
- Avoidable evening, Saturday and Sunday assignments.

Do not make Saturday, Sunday, or evening sessions invalid solely because of
their time. Apply any default avoidance only through configurable soft weights,
and waive the matching default weight when the lecturer explicitly prefers the
day or slot. Do not automatically penalize consecutive valid sessions or
movement between university buildings.

Official time slots already provide adequate transition time.

Soft-constraint weights must be configurable and recorded with every run.

Each scoring function should be independently testable.

---

## 17. Fitness and Cost

Prefer a cost model in which lower values are better.

Example structure:

    total_cost =
        hard_penalty
        + lecturer_preference_cost
        + gap_cost
        + room_waste_cost
        + distribution_cost

Hard penalties must dominate all possible soft improvements.

A valid timetable must always rank better than an invalid timetable.

Do not rely on an arbitrary hard penalty without checking whether accumulated
soft scores could exceed it.

Preferred approaches include:

- Rejecting invalid individuals.
- Lexicographic comparison:
  1. Hard-violation count.
  2. Soft cost.
- A provably dominant hard-penalty value.

Recommended evaluation result:

    EvaluationResult(
        hard_violation_count=0,
        hard_violations=[],
        soft_cost=125.0,
        soft_breakdown={
            "lecturer_preferences": 25.0,
            "room_capacity_waste": 60.0,
            "schedule_gaps": 40.0,
        },
        total_cost=125.0,
    )

Do not return only one unexplained fitness number.

Store a detailed score breakdown for experimentation and reporting.

---

## 18. Population Initialization

Precompute feasible domains for each course section.

Example:

    feasible_assignments[section_code] = [
        Assignment(day, slot, room),
        ...
    ]

An assignment belongs to the feasible domain only when its local constraints
pass:

- Slot supports the course type.
- Slot has the required duration.
- Room type is compatible.
- Room capacity is sufficient.
- Room is active.
- Mandatory lecturer restrictions are respected.

Global conflicts between different genes may still exist and must be handled by
evaluation or repair.

When a section has no feasible assignment:

- Stop before starting the GA.
- Return a clear diagnostic.
- Include the section code and reason.

Do not generate thousands of known-invalid genes and expect the fitness
function to repair everything.

Use a mixture of:

- Random feasible initialization.
- Heuristic initialization.
- Diversity preservation.

Avoid producing identical initial individuals.

---

## 19. Selection

Implement at least one clear selection strategy.

Tournament selection is recommended because it is:

- Simple.
- Efficient.
- Easy to test.
- Compatible with minimization cost.

Selection must use the documented comparison rule.

When using lexicographic evaluation:

1. Prefer fewer hard violations.
2. When equal, prefer lower soft cost.

Do not compare only raw fitness when hard and soft components are stored
separately.

Selection must not mutate individuals.

---

## 20. Crossover

Crossover must preserve one gene per course section.

After crossover:

- No section may be missing.
- No section may appear twice.
- Fixed lecturer and course-section data must remain unchanged.
- Only assignable scheduling values may come from parents.

Suitable strategies include:

- One-point crossover on a stable section order.
- Two-point crossover.
- Uniform crossover by section.
- Group-aware crossover by lecturer or course-section subsets.

Do not use crossover designs that change the meaning or identity of gene
positions.

After crossover:

1. Validate chromosome structure.
2. Evaluate hard conflicts.
3. Repair when practical.
4. Preserve diversity.

Crossover must be deterministic when supplied with a controlled random
generator and seed.

---

## 21. Mutation

Mutation may change:

- Day.
- Time slot.
- Room.
- A complete feasible assignment.

Mutation must not change:

- Course-section identity.
- Primary lecturer.
- Course identity.
- Session duration.
- Required room type.
- Scheduling student count.

Prefer selecting mutation values from the precomputed feasible domain.

Possible mutation operations:

- Change room while keeping day and slot.
- Change day and compatible slot.
- Change the full assignment.
- Swap compatible assignments between two sections when valid.
- Move a conflicting gene to a feasible alternative.

Mutation must respect the configured mutation probability.

Do not apply every mutation type to every individual unconditionally.

---

## 22. Repair

Repair should target common hard conflicts.

Possible repair order:

1. Missing or structurally invalid gene.
2. Invalid slot compatibility.
3. Invalid room type.
4. Insufficient capacity.
5. Mandatory lecturer restriction.
6. Lecturer conflict.
7. Room conflict.

Repair should:

- Use feasible-domain candidates.
- Prefer changes with low soft cost.
- Avoid infinite loops.
- Have a configurable attempt limit.
- Return whether repair succeeded.
- Preserve the course-section identity.

When repair fails:

- Keep the individual as invalid with explicit violations.
- Or discard and regenerate it.

Do not silently remove a course section from the chromosome.

---

## 23. Elitism and Diversity

Use elitism to preserve a small number of best individuals.

Do not copy so many elite individuals that population diversity collapses.

Track diversity using one or more simple indicators:

- Unique chromosome count.
- Assignment-distance estimate.
- Duplicate ratio.
- Gene-level variation.

When the population converges too early, possible responses include:

- Increase mutation temporarily.
- Inject new feasible random individuals.
- Reduce elite count.
- Use diversity-aware survivor selection.

Any adaptive behavior must be documented and testable.

---

## 24. Stopping Conditions

Supported stopping conditions may include:

- Maximum generation count.
- Time limit.
- No improvement for a configured number of generations.
- A valid timetable reaching a target soft cost.
- Explicit cancellation by the caller.

The algorithm should safely preserve the best-so-far individual when stopped.

A cancelled run should not be reported as a technical failure.

Differentiate:

- Completed normally.
- Stopped by time limit.
- Stopped by stagnation.
- Cancelled by user.
- Failed because of invalid input.
- Failed because of an unexpected error.

---

## 25. Reproducibility

All randomness must come from an injected or locally controlled random
generator.

Do not use uncontrolled global randomness throughout the module.

A run should record:

- Random seed.
- Population size.
- Generation count.
- Mutation rate.
- Crossover rate.
- Soft-constraint weights.
- Stopping conditions.
- Input-data version.

Given the same:

- Validated input.
- Configuration.
- Seed.
- Code version.

the algorithm should produce reproducible or meaningfully equivalent results.

Unit tests must use fixed seeds.

---

## 26. Algorithm Input Contract

The GA should receive normalized domain data, not raw CSV rows.

Suggested input concepts:

    GeneticAlgorithmInput
    ├── course_sections
    ├── lecturers
    ├── rooms
    ├── time_slots
    ├── lecturer_preferences
    ├── mandatory_lecturer_restrictions
    ├── room_unavailability
    └── configuration

Raw values such as Vietnamese CSV labels should be normalized before entering
the GA module.

The GA module must not:

- Open CSV files.
- Parse CSV rows.
- Query the database.
- Read environment variables directly.
- Depend on web request objects.

---

## 27. Algorithm Output Contract

The result should include more than a timetable list.

Suggested output:

    GeneticAlgorithmResult
    ├── status
    ├── best_candidate
    ├── evaluation
    ├── generation_count
    ├── execution_time
    ├── seed
    ├── stop_reason
    ├── fitness_history
    └── diagnostics

Each timetable assignment should include:

- Course-section code.
- Primary lecturer code.
- Day of week.
- Slot code.
- Start period.
- End period.
- Room code.
- Course type.
- Required room type.
- Scheduling student count.

Do not create dated session occurrences inside the core GA result unless the
design explicitly requires a separate expansion step.

---

## 28. Error Handling

Use explicit domain exceptions or result types for expected failures.

Examples:

- No feasible room for a course section.
- No compatible time slot.
- Empty course-section dataset.
- Invalid GA configuration.
- Invalid mutation rate.
- Invalid crossover rate.
- Missing lecturer reference.
- Missing room reference.

Do not hide domain errors behind a generic message such as:

    Genetic Algorithm failed.

Return actionable diagnostics.

Unexpected errors may be logged by the application layer, but the GA module
must not depend on a framework logger.

---

## 29. Performance

The initial target is approximately:

- 20 lecturers.
- 100–200 course sections.
- About 200 genes per chromosome.
- Approximately 1,500–3,000 dated occurrences after calendar expansion.

Optimize the chromosome and evaluation for course-section genes, not expanded
occurrences.

Use indexes such as:

- Assignments by lecturer and day.
- Assignments by room and day.
- Compatible slots by course type and duration.
- Compatible rooms by room type and capacity.
- Preferences by lecturer.

Avoid repeatedly scanning the complete dataset for every small check when an
index can be prepared once.

Do not sacrifice correctness for premature micro-optimization.

Measure performance before introducing complex caching.

---

## 30. Logging and Metrics

The module may expose structured progress information.

Useful metrics include:

- Current generation.
- Best hard-violation count.
- Best soft cost.
- Average population cost.
- Number of unique individuals.
- Repair attempts.
- Repair success rate.
- Execution time.

Do not print directly to standard output from core algorithm functions.

Use callbacks, events, return values, or an injected progress reporter.

Do not log every gene in every generation during normal execution.

---

## 31. Testing Requirements

At minimum, unit tests must cover:

### Time and overlap

- Same lecturer in the same slot.
- Same lecturer in partially overlapping slots.
- Same room in the same slot.
- Same room in partially overlapping slots.
- Periods 1–5 versus periods 2–6.
- Non-overlapping consecutive sessions.
- Valid weekend schedules.

### Course types

- Theory with a three-period slot.
- Practice with periods 1–5.
- Practice with periods 1–6.
- Practice with periods 2–6.
- Integrated class with five periods.
- Integrated class with six periods.
- Invalid course-type and slot combination.

### Rooms

- Compatible room type.
- Incompatible room type.
- Sufficient capacity.
- Insufficient capacity.
- Standard-room preference.
- Large-room soft penalty.
- Large room remaining valid when needed.

### Lecturer rules

- One lecturer teaching multiple non-overlapping classes.
- One lecturer teaching different courses.
- Consecutive sessions remaining valid.
- Preferred weekend teaching.
- Undesired weekday penalty.
- Mandatory restriction as a hard constraint.
- Non-mandatory preference remaining soft.

### Genetic operations

- Population initialization.
- Structural chromosome validity.
- Selection reproducibility.
- Crossover preserving all course sections.
- Mutation preserving fixed fields.
- Repair resolving common conflicts.
- Repair failure returning diagnostics.
- Elitism preserving the best candidate.
- Fixed-seed reproducibility.
- Safe stopping with best-so-far result.

### Evaluation

- Valid candidate has zero hard violations.
- Invalid candidate never outranks a valid candidate.
- Soft-cost breakdown matches the total.
- Configurable weights affect ranking.
- Default evening/weekend avoidance is configurable and an explicit lecturer preference waives the matching default penalty.

Use small datasets whose expected solution can be checked manually.

---

## 32. Out-of-Scope Algorithm Features

Do not implement these features unless the approved requirements change:

- Automatic lecturer-to-course assignment.
- Student course registration.
- Student accounts.
- Individual student timetables.
- Student availability matching.
- Automatic makeup-session selection.
- Automatic negotiation with students.
- Practice-class group splitting.
- Multiple primary lecturers per course section.
- Automatic substitute-lecturer assignment.
- Automatic schedule segmentation by date range.
- Automatic movement of holiday sessions.
- Travel-time optimization between buildings.
- Guaranteed globally optimal solutions.
- Full university-scale production optimization.

---

## 33. Code Quality

- Use clear type annotations.
- Use dataclasses or equivalent typed domain objects.
- Keep pure evaluation functions free of side effects.
- Separate initialization, evaluation, selection, crossover, mutation, repair,
  and stopping logic.
- Avoid large functions handling the entire algorithm.
- Avoid unstructured nested dictionaries where typed objects are clearer.
- Avoid mutable global state.
- Inject random generators and configuration.
- Document non-obvious algorithm decisions.
- Keep constraint identifiers stable.
- Remove debugging prints.
- Do not catch broad exceptions without re-raising or returning diagnostics.
- Do not duplicate business rules from unrelated modules.

Prefer correctness and explainability over clever but opaque code.

---

## 34. Change Discipline

When changing the GA model or a constraint:

1. Review the latest URS and SRS.
2. Confirm whether the rule is hard or soft.
3. Update the relevant domain type.
4. Update feasible-domain generation.
5. Update evaluation.
6. Update repair when applicable.
7. Update sample CSV data when applicable.
8. Add or update tests.
9. Record the change in algorithm documentation.
10. Check whether previously stored experiment results remain comparable.

Do not change chromosome meaning without documenting migration and test impact.

---

## 35. Definition of Done

A Genetic Algorithm change is complete when:

- It follows the latest URS and SRS.
- It preserves fixed teaching assignments.
- It uses one base weekly gene per course section for the MVP.
- It selects only configured valid time slots.
- It correctly detects partial overlaps.
- It enforces room type and capacity.
- It treats weekends as valid days.
- It distinguishes mandatory restrictions from soft preferences.
- It provides a detailed hard/soft evaluation breakdown.
- It is reproducible with a fixed seed.
- It remains independent of HTTP, ORM, and CSV parsing.
- Relevant unit tests pass.
- Performance is acceptable for 100–200 course sections.
- No hard constraint is silently relaxed.
