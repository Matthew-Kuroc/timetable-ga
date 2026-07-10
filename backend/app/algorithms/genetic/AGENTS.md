# Genetic Algorithm AGENTS.md

## 1. Scope

This file defines instructions for AI coding agents modifying files under:

```text
backend/app/algorithms/genetic/
```

It extends:

1. `/AGENTS.md`
2. `/backend/AGENTS.md`

All repository and backend rules remain active.

This file contains only rules specific to the timetable Genetic Algorithm.

---

## 2. Algorithm responsibility

This module is responsible for generating and evaluating teaching-timetable
candidates using a Genetic Algorithm.

It may contain:

- Scheduling-domain input structures.
- Gene and chromosome representations.
- Population initialization.
- Constraint evaluation.
- Fitness evaluation.
- Selection.
- Crossover.
- Mutation.
- Elitism.
- Repair mechanisms.
- Stopping conditions.
- Run statistics.
- Deterministic random-number handling.
- Algorithm-specific tests.

It must not contain:

- FastAPI routes.
- HTTP request or response handling.
- React or frontend code.
- Authentication.
- Direct UI formatting.
- Spreadsheet presentation logic.
- Uncontrolled database transactions.
- Business workflows unrelated to timetable optimization.

---

## 3. Sources of truth

Before implementing or changing an algorithm rule, read:

1. The assigned GitHub Issue.
2. `docs/requirements/URS.md`.
3. `docs/requirements/SRS.md`.
4. Relevant algorithm-design documents.
5. Existing constraint tests.
6. Existing implementation and experiment results.
7. This file.

Do not derive a business constraint only from an example dataset.

Do not treat an experimental idea as a confirmed requirement.

When a rule is unclear, expose the ambiguity instead of hard-coding an
assumption.

---

## 4. Known unresolved rules

The following may still require confirmation:

- Which student-count field is used for room-capacity checking.
- Whether room-capacity shortage is always a hard constraint.
- Whether preliminary schedules may temporarily use undersized rooms.
- Practical-class duration and room requirements.
- Exceptional time slots such as non-standard period ranges.
- Minimum spacing for classes that meet multiple times per week.
- Final weights for soft constraints.
- Whether all preferred lecturer slots have equal priority.
- Whether evening and weekend penalties differ by course type.

Implement unresolved rules through centralized configuration or policies.

Do not scatter provisional values across operators or fitness functions.

Every temporary rule must be:

- Named clearly.
- Documented as provisional.
- Covered by a test.
- Easy to replace.

---

## 5. Design goals

The algorithm should prioritize:

1. Correctness.
2. Validity under hard constraints.
3. Testability.
4. Reproducibility.
5. Clarity.
6. Measurable quality.
7. Performance after measurement.

A timetable with a better fitness score but hard-constraint violations must
not be treated as preferable to a valid timetable.

The algorithm does not need to guarantee the global optimum.

It should produce a useful, explainable and measurable solution within the
project’s practical limits.

---

## 6. Separation from infrastructure

The Genetic Algorithm should operate on normalized domain data.

It should not require:

- An HTTP request.
- A FastAPI dependency.
- An active ORM session throughout the run.
- A browser session.
- Frontend-specific field names.

Preferred flow:

```text
Database or imported data
        ↓
Backend service normalizes input
        ↓
Algorithm receives domain input and configuration
        ↓
Algorithm returns structured result and metrics
        ↓
Backend service persists or exposes the result
```

Do not perform database queries inside fitness evaluation or genetic
operators.

Required data should be loaded and normalized before the run starts.

---

## 7. Public algorithm interface

The module should expose a small, clear interface.

A conceptual interface may resemble:

```python
result = generate_timetable(
    problem=problem,
    config=config,
)
```

The exact API should follow existing code.

Inputs should clearly represent:

- Lecturers.
- Rooms.
- Course sections.
- Required sessions.
- Time slots.
- Availability.
- Preferences.
- Constraint configuration.
- Algorithm parameters.
- Random seed.

The result should clearly represent:

- Best candidate.
- Validity.
- Hard-constraint violations.
- Soft-constraint penalties.
- Fitness.
- Number of generations.
- Execution time.
- Random seed.
- Relevant convergence metrics.

Do not return a raw nested list without a documented structure.

---

## 8. Domain identifiers

Use stable identifiers for:

- Lecturer.
- Room.
- Course section.
- Time slot.
- Session occurrence.

Do not use display names as unique identifiers.

Examples:

```text
lecturer_code
room_code
section_code
slot_code
session_id
```

Display names may change or be duplicated.

Algorithm data structures should keep identifier meaning explicit.

---

## 9. Gene representation

A gene should represent one clearly defined scheduling decision.

A possible conceptual gene may associate:

```text
Required class session
        +
Assigned time slot
        +
Assigned room
```

The final representation must be documented before relying on it.

Each gene must preserve enough information to identify:

- The course section.
- The required session occurrence.
- The lecturer.
- The assigned time slot.
- The assigned room.
- Relevant week pattern if applicable.

Avoid duplicating data that can be safely resolved from immutable problem
input, but do not make the representation impossible to understand or test.

---

## 10. Chromosome invariants

A chromosome represents one timetable candidate.

Unless requirements specify otherwise, maintain invariants such as:

- Every required session appears exactly once.
- No unrelated session is introduced.
- Session identity is not lost during crossover.
- Session identity is not duplicated during mutation.
- Assigned rooms and time slots reference known values.
- Chromosome length remains consistent with required sessions.

Operators must preserve invariants or be followed by a verified repair step.

Do not rely only on fitness penalties to detect structurally corrupted
chromosomes.

---

## 11. Problem preprocessing

Precompute immutable lookup data before evaluating populations where useful.

Examples:

- Valid rooms by course type.
- Valid rooms by capacity policy.
- Valid slots by session duration.
- Lecturer unavailable slots.
- Room unavailable slots.
- Course-section-to-lecturer mapping.
- Session identifiers.
- Time-slot overlap relationships.

Do not repeat expensive, deterministic lookups for every gene in every
generation when they can be prepared once.

Preprocessing must not change the meaning of source data.

Precomputed structures should be covered by tests when they affect validity.

---

## 12. Hard constraints

Hard constraints determine whether a timetable is valid.

At minimum, evaluate the confirmed forms of:

### HC-01 — Lecturer conflict

A lecturer must not teach two overlapping sessions at the same time.

### HC-02 — Room conflict

A room must not host two overlapping sessions at the same time.

### HC-03 — Required session count

Each course section must receive exactly its required number of sessions.

### HC-04 — Room type

The assigned room type must satisfy the course-section requirement.

### HC-05 — Room capacity

The assigned room must satisfy the confirmed capacity policy.

The capacity policy is not final until the related business question is
resolved.

### HC-06 — Lecturer availability

A lecturer must not be assigned to a confirmed unavailable slot.

### HC-07 — Room availability

A room must not be assigned during an unavailable slot.

### HC-08 — Valid time slot

A session must use an active time slot compatible with its required duration.

### HC-09 — Valid references

Every gene must reference known domain entities.

Additional hard constraints may be added only when supported by requirements.

---

## 13. Hard-constraint evaluation

Hard-constraint evaluation must be available independently of total fitness.

The algorithm result should expose structured violations, for example:

```python
HardConstraintViolation(
    code="LECTURER_TIME_CONFLICT",
    entities=("GV001", "SECTION01", "SECTION02"),
    slot_code="MON_AM_01",
    message="Lecturer GV001 is assigned to overlapping sessions.",
)
```

The exact class is implementation-dependent.

Each violation should ideally provide:

- Machine-readable code.
- Affected entities.
- Relevant time slot or assignment.
- Human-readable explanation.
- Count or severity if applicable.

Do not return only:

```python
is_valid = False
```

without diagnostic information.

A candidate is valid only when the authoritative hard-constraint violation
count is zero.

---

## 14. Soft constraints

Soft constraints improve timetable quality without determining basic
validity.

Potential soft constraints include:

- Lecturer preferred slots.
- Maximum desired teaching days.
- Maximum desired consecutive sessions.
- Fewer gaps between a lecturer’s sessions.
- Balanced teaching distribution across the week.
- Reduced evening assignments.
- Reduced Saturday or Sunday assignments.
- Better room-size utilization.
- Fewer unnecessary room changes.
- Better spacing between repeated weekly sessions.

Only confirmed or explicitly experimental soft constraints may be used.

Each soft constraint must have:

- A stable identifier.
- A documented calculation.
- A centralized weight.
- Unit tests.
- Metrics that can be inspected independently.

Do not hide all soft penalties inside one unexplained number.

---

## 15. Fitness structure

Keep hard and soft evaluation separate.

A conceptual structure may be:

```text
hard_violation_count
hard_penalty
soft_penalty
fitness
```

One possible model is:

```text
fitness = base_score - hard_penalty - soft_penalty
```

The actual formula must be documented and tested.

Requirements:

- Hard violations must dominate soft improvements.
- A soft preference must never compensate for a hard violation.
- Fitness direction must be consistent: clearly maximize or clearly minimize.
- No unexplained magic constants.
- Weights must be centralized.
- Individual penalty components should be inspectable.

Prefer returning a breakdown such as:

```python
FitnessResult(
    total=...,
    hard_penalty=...,
    soft_penalty=...,
    components={
        "lecturer_conflict": ...,
        "room_conflict": ...,
        "lecturer_preference": ...,
    },
)
```

The exact implementation should fit existing conventions.

---

## 16. Configuration

Algorithm configuration may include:

- Population size.
- Number of generations.
- Crossover rate.
- Mutation rate.
- Elitism count or rate.
- Selection method.
- Tournament size if applicable.
- Random seed.
- Stagnation limit.
- Time limit.
- Soft-constraint weights.
- Repair settings.

Validate configuration before starting.

Examples of invalid input:

- Population size below the algorithm minimum.
- Negative generations.
- Rates outside `[0, 1]`.
- Elitism larger than population.
- Invalid selection method.
- Negative constraint weight.
- Empty scheduling problem.

Do not silently correct invalid configuration without reporting it.

Default values must be centralized and documented.

---

## 17. Population initialization

Initialization should produce diverse candidates while respecting structural
invariants.

Where practical, prefer assigning genes from known compatible options:

- Valid time slots.
- Compatible room types.
- Available rooms.
- Plausible room capacities.

Do not guarantee validity unless the initializer actually checks all hard
constraints.

A partially constraint-aware initializer may reduce search time, but its
behavior must be clear.

Initialization must:

- Use the supplied random generator.
- Avoid hidden global randomness.
- Preserve every required session.
- Fail clearly when a session has no possible assignment.

Do not enter an endless retry loop when no feasible assignment exists.

---

## 18. Selection

Selection must be implemented as an explicit strategy.

Possible strategies include:

- Tournament selection.
- Rank selection.
- Roulette-wheel selection where fitness conditions make it safe.

Do not assume roulette-wheel selection works correctly with negative or
unbounded fitness values.

Selection tests should check:

- Correct output count.
- Valid candidate references.
- Behavior with equal fitness.
- Behavior with minimal populations.
- Deterministic behavior with a fixed seed where applicable.

Do not mutate selected parents accidentally.

---

## 19. Crossover

Crossover must preserve session identity.

The operator must not:

- Drop a required session.
- Duplicate a required session.
- Introduce unknown session identifiers.
- Modify parents in place unless the design explicitly requires and documents
  it.

Potential strategies must be evaluated against the chromosome representation.

After crossover:

- Verify structural invariants.
- Repair only when a defined repair strategy exists.
- Preserve deterministic behavior with a fixed random seed.

Tests should cover:

- Crossover rate zero.
- Crossover rate one.
- Minimal chromosome size.
- Parents with different assignments.
- Parent immutability.
- Child session completeness.

---

## 20. Mutation

Mutation should make a bounded scheduling change.

Possible mutations include:

- Change a session’s time slot.
- Change its room.
- Change both room and time slot.
- Swap assignments when representation supports it.

Mutation must not alter session identity.

Mutation should choose from valid domain identifiers.

Where practical, choose compatible values rather than arbitrary invalid
values, but do not misrepresent a heuristic as a complete validity guarantee.

Tests should cover:

- Mutation rate zero.
- Mutation rate one.
- No valid alternative assignment.
- Fixed-seed behavior.
- Chromosome invariants after mutation.
- Parent or input immutability where expected.

---

## 21. Elitism

Elitism may preserve top candidates between generations.

Requirements:

- Validate elite count.
- Avoid accidental shared mutable references.
- Do not allow elite count to consume the entire population unless explicitly
  intended.
- Preserve candidate statistics consistently.
- Document whether elites are copied or referenced.

Tests should verify that the best eligible candidates survive when elitism is
enabled.

---

## 22. Repair mechanisms

A repair mechanism may correct structural or scheduling violations.

A repair step must:

- Have a defined scope.
- Be deterministic under the supplied random seed where randomness is used.
- Never remove required sessions.
- Never hide unresolved violations.
- Return or expose repair outcomes.
- Be independently testable.

Do not create an unbounded repair loop.

Do not silently modify a candidate without preserving traceability during
debugging or experiments.

Repair does not replace final hard-constraint validation.

---

## 23. Randomness and reproducibility

All random behavior must use an explicitly controlled random-number generator.

Do not mix uncontrolled calls such as:

```python
random.random()
numpy.random.random()
```

across the implementation without a coordinated seed strategy.

Prefer passing a random generator or context to operators.

Every run should record its random seed.

With the same:

- Input data.
- Configuration.
- Implementation version.
- Random seed.

the algorithm should be reproducible to the degree supported by the execution
environment.

Tests that depend on randomness must use a fixed seed.

---

## 24. Stopping conditions

Possible stopping conditions include:

- Maximum generations reached.
- Zero hard violations and acceptable quality reached.
- No improvement for a configured number of generations.
- Time limit reached.
- External cancellation when later supported.

Stopping conditions must be explicit and recorded in results.

Do not stop only because one candidate has a high total fitness if hard
violations remain.

Prevent infinite loops by enforcing at least one finite stopping condition.

---

## 25. Run metrics

Collect metrics useful for experiments and debugging.

Potential metrics:

- Population size.
- Generation count.
- Best fitness per generation.
- Average fitness per generation.
- Hard-violation count per generation.
- Soft penalty per generation.
- Generation where the best candidate was found.
- Execution time.
- Random seed.
- Crossover count.
- Mutation count.
- Repair count.
- Stopping reason.

Do not store excessive per-candidate data without a demonstrated need.

Metrics should not change algorithm behavior.

---

## 26. Performance rules

Correctness comes before optimization.

Before optimizing:

1. Establish deterministic tests.
2. Verify hard constraints.
3. Measure execution time.
4. Profile representative data.
5. Identify the actual bottleneck.
6. Optimize the measured area.

Potential safe optimizations include:

- Precomputed lookup maps.
- Incremental conflict counts when proven correct.
- Avoiding repeated immutable calculations.
- Efficient overlap indexes.
- Limiting unnecessary object copying.

Do not introduce difficult caching that risks stale or incorrect fitness
results without tests proving correctness.

Do not query the database from the fitness loop.

---

## 27. Immutability and side effects

Prefer predictable data flow.

Operators should clearly document whether they:

- Return new candidates.
- Modify candidates in place.
- Share gene objects.
- Copy fitness metadata.

Avoid accidental mutation of:

- Parent chromosomes.
- Problem input.
- Configuration.
- Previously recorded best candidates.

Tests should detect shared-reference errors.

---

## 28. Failure handling

Fail clearly when the scheduling problem is impossible to initialize or
contains invalid input.

Examples:

- No active time slots.
- A required practical class has no compatible room.
- A course section references an unknown lecturer.
- A required session has no possible assignment.
- Population configuration is invalid.

Do not continue with corrupted or incomplete problem data.

Distinguish:

- Invalid input.
- No feasible solution found within limits.
- Internal algorithm failure.
- Cancelled execution.

These outcomes must not all be represented as a generic failure.

---

## 29. Algorithm testing

Algorithm tests should use small, understandable fixtures.

A human should be able to reason about expected outcomes.

### 29.1. Domain tests

Test:

- Session construction.
- Identifier uniqueness.
- Time-slot overlap.
- Compatible rooms.
- Invalid references.

### 29.2. Hard-constraint tests

For each hard constraint, include:

- Valid case.
- Single violation.
- Multiple violations.
- Boundary case.

Examples:

- Same lecturer, different slots.
- Same lecturer, same slot.
- Same room, same slot.
- Room capacity equal to required capacity.
- Room capacity below required capacity.
- Lecturer unavailable slot.
- Inactive time slot.

Capacity tests must reflect the currently configured capacity policy and be
updated when the business decision changes.

### 29.3. Soft-constraint tests

Test each component separately.

Verify:

- No violation gives zero or expected penalty.
- One violation gives the documented penalty.
- Multiple violations aggregate correctly.
- Weight changes affect only the intended component.

### 29.4. Fitness tests

Verify:

- Breakdown values.
- Total calculation.
- Hard penalties dominate soft benefits.
- Invalid candidates are not marked valid.
- Fitness direction remains consistent.

### 29.5. Operator tests

Test selection, crossover, mutation and elitism independently.

Check structural invariants after each operator.

### 29.6. Reproducibility tests

With a fixed seed:

- Initialization should be reproducible.
- Operators should be reproducible.
- A small complete run should be reproducible where practical.

### 29.7. Integration tests

Use a small complete scheduling problem.

Verify that:

- The algorithm terminates.
- The result has all required sessions.
- The result contains known entities.
- The final hard-constraint checker runs.
- Metrics are present.
- The stopping reason is recorded.

Do not require an exact global optimum unless the fixture is small enough for
that expectation to be proven.

---

## 30. Experiment integrity

When comparing algorithm configurations:

- Use the same input dataset.
- Record each random seed.
- Run multiple seeds where appropriate.
- Record configuration values.
- Record implementation version or commit.
- Compare validity before soft quality.
- Report execution environment when performance is discussed.

Do not compare one lucky run against another method and present it as a
general conclusion.

Do not alter the dataset between configurations without documenting it.

---

## 31. Documentation requirements

When changing the chromosome, fitness or a major operator, update relevant
documentation.

Document:

- Representation.
- Invariants.
- Fitness direction.
- Constraint definitions.
- Weight meanings.
- Operator behavior.
- Configuration defaults.
- Metrics.
- Known limitations.

Do not let implementation and algorithm documentation describe different
formulas.

---

## 32. Prohibited actions

Do not:

- Implement the entire GA in one large function.
- Query the database inside fitness evaluation.
- Depend on FastAPI objects.
- Use hidden global random state.
- Scatter weights as magic numbers.
- Mark a candidate valid when hard violations remain.
- Allow soft rewards to cancel hard violations.
- Drop or duplicate required sessions during operators.
- Modify parents unexpectedly.
- Hide constraint violations after repair.
- Add an unverified optimization that changes results.
- claim optimality without proof.
- claim tests passed without running them.
- hard-code unresolved capacity rules as permanent behavior.

---

## 33. Genetic Algorithm Definition of Done

An algorithm task is complete when applicable conditions are satisfied:

- The requirement or experiment objective is clear.
- Data structures and invariants are documented.
- Hard and soft logic remain separated.
- All required sessions are preserved.
- Final hard-constraint validation is performed.
- Randomness uses the configured seed strategy.
- Relevant unit tests are added.
- Existing deterministic tests still pass.
- Metrics are updated when behavior changes.
- Performance claims have measurements.
- Documentation matches the implementation.
- Temporary assumptions are reported.
- No infrastructure-specific dependency has leaked into the algorithm core.

---

## 34. Final report for algorithm changes

After changing Genetic Algorithm code, report:

### Algorithm change

Describe the representation, constraint, fitness or operator that changed.

### Invariants

State which chromosome invariants were checked.

### Fitness impact

State how hard penalties, soft penalties or total fitness changed.

### Reproducibility

State the seed used for tests or experiments.

### Verification

List:

- Tests run.
- Dataset or fixture used.
- Results.
- Checks not run.

### Performance

Provide measurements only if performance was tested.

### Assumptions

List unresolved business rules or temporary configuration choices.
