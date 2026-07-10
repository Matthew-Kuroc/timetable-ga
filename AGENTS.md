# AGENTS.md

## 1. Purpose

This file defines repository-wide instructions for AI coding agents working
on `timetable-ga`.

These rules apply to every directory in the repository unless a more specific
`AGENTS.md` exists in a subdirectory.

The goal is to ensure that every change is:

- Grounded in documented requirements.
- Limited to the assigned task.
- Easy to review and test.
- Safe for the repository and user data.
- Consistent with the project architecture.
- Appropriate for a student internship project.

---

## 2. Project overview

`timetable-ga` is a web application for generating university teaching
timetables using a Genetic Algorithm.

The main users are:

- Training Department staff or timetable managers.
- Lecturers.
- Technical administrators.

The system is expected to support:

- CSV data import and validation.
- Genetic Algorithm configuration and execution.
- Hard and soft scheduling constraints.
- Timetable views by lecturer, room and course section.
- Lecturer weekly timetable views.
- Timetable adjustment requests.
- Conflict checking.
- CSV and Excel export.
- Experiment and run-history tracking.

Student course registration is outside the scope of this version.

See `README.md` for the project overview.

---

## 3. Sources of truth

Before implementing a task, read the relevant sources in this order:

1. The assigned GitHub Issue and its acceptance criteria.
2. `docs/requirements/URS.md`.
3. `docs/requirements/SRS.md`.
4. The nearest applicable `AGENTS.md`.
5. Relevant architecture, database, API or testing documents.
6. Existing code and tests.
7. `README.md`.

If a referenced document does not exist yet, continue with the available
sources and explicitly report what is missing.

Do not treat README content marked as planned or expected as already
implemented.

---

## 4. Requirement conflicts and ambiguity

Do not invent business rules.

When requirements are unclear or contradictory:

1. Identify the exact ambiguity.
2. Check the Issue, URS, SRS and current code.
3. Explain the possible interpretations.
4. State the impact of each interpretation.
5. Ask for confirmation before implementing behavior that depends on it.

A temporary assumption must:

- Be stated explicitly.
- Be easy to change.
- Be placed in centralized configuration where appropriate.
- Never be presented as a confirmed business rule.

Known topics that may still require confirmation include:

- The room-capacity rule.
- Which student-count field is used for capacity checking.
- The approval workflow for timetable changes.
- The deadline for moving an entire recurring schedule.
- Make-up class rules after a suspended session.
- Practical-class scheduling rules.
- Exceptional teaching time slots.
- Official production CSV structures.
- Initial weights for soft constraints.

---

## 5. Repository state

The repository may still be in an initialization stage.

Do not assume that the following already exist:

- FastAPI backend.
- React frontend.
- PostgreSQL database.
- Database migrations.
- Docker Compose.
- Authentication.
- Automated tests.
- Lint or formatting configuration.
- GitHub Actions.
- Genetic Algorithm implementation.

Inspect the repository before proposing or creating files.

Do not generate the entire planned project structure for a small task.

Create only the files required for the current Issue.

---

## 6. Required workflow

Before changing files:

1. Check the current Git state.
2. Read the assigned Issue.
3. Read the applicable requirement documents.
4. Inspect existing code and tests.
5. Identify affected files.
6. Present a short implementation plan for non-trivial tasks.
7. Report ambiguities before relying on assumptions.

Useful Git checks:

```bash
git status
git branch --show-current
git log --oneline -5
```

Never overwrite uncommitted user changes.

---

## 7. Scope discipline

Make the smallest change that satisfies the assigned requirements.

Do not:

- Add unrelated features.
- Perform large refactors during a small feature task.
- Rename or reformat unrelated files.
- Introduce speculative abstractions.
- Add infrastructure that the current task does not require.
- Replace existing frameworks without explicit approval.
- Duplicate existing business logic.
- Create files only because they appear in a planned folder tree.

Prefer simple, readable and testable code over clever code.

---

## 8. Global business rules

The following principles apply across the system:

- A lecturer must not teach two classes at the same time.
- A room must not host two classes at the same time.
- Every course section must receive its required sessions.
- Room type must match the course-section requirement.
- Manual timetable changes must be checked for conflicts.
- Hard constraints must never be silently ignored.
- A high fitness score does not make a timetable valid when hard constraints
  are violated.
- Authorization must be enforced by the backend, not only by hiding frontend
  controls.

Detailed algorithm rules belong in:

```text
backend/app/algorithms/genetic/AGENTS.md
```

---

## 9. Technology boundaries

The expected primary stack is:

- Backend: Python and FastAPI.
- Frontend: React and TypeScript.
- Database: PostgreSQL.
- Algorithm: Python.
- Testing: pytest and appropriate frontend testing tools.
- Collaboration: GitHub Issues and Pull Requests.

Do not replace a primary technology without explicit approval.

Before adding a production dependency, explain:

- The problem it solves.
- Why existing dependencies are insufficient.
- Its maintenance and security implications.
- Whether a simpler alternative exists.

Do not add a dependency merely to avoid writing a small amount of clear code.

---

## 10. Security and data safety

Never commit:

```text
.env
.env.local
.env.production
*.pem
*.key
credentials.json
secret.json
access tokens
API keys
database passwords
production database dumps
unapproved personal data
```

Do not:

- Store passwords in plain text.
- log secrets or complete authentication tokens.
- expose internal stack traces to users.
- trust file names, MIME types or client-provided identifiers without
  validation.
- use real personal data as sample data unless its use has been approved.

Use `.env.example` only for variable names and safe example values.

---

## 11. Git safety

Do not work directly on `main`.

Use task-based branches, for example:

```text
feature/TKB-010-upload-csv
bugfix/TKB-020-room-conflict
docs/TKB-030-update-requirements
test/TKB-040-add-constraint-tests
refactor/TKB-050-fitness-evaluator
chore/TKB-060-project-configuration
```

Do not run destructive Git commands without explicit user approval.

Examples of destructive commands:

```bash
git reset --hard
git clean -fd
git restore .
git checkout -- .
git push --force
```

Do not push, merge, delete branches or create releases unless the user
explicitly requests that action.

---

## 12. Testing and verification

Every behavior change should have appropriate verification.

Depending on the task, this may include:

- Unit tests.
- Integration tests.
- API tests.
- Component tests.
- Regression tests.
- Constraint tests.
- Build, lint or type checks.

Do not claim that tests passed unless the commands were actually run.

If tests cannot be run, report:

- Which checks were not run.
- Why they could not be run.
- What command should be run later.
- What risk remains.

Do not delete, weaken or skip a test merely to make the test suite pass.

Specific commands are defined in local `AGENTS.md` files after the relevant
tooling has been configured.

---

## 13. Definition of done

A task is complete only when:

- Its acceptance criteria are satisfied.
- The implementation stays within scope.
- Relevant tests have been added or updated.
- Required checks have passed, or missing checks are clearly reported.
- Existing behavior has not been unintentionally broken.
- No secrets or unauthorized personal data are included.
- Error cases and permissions are handled appropriately.
- Documentation is updated when behavior changes.
- Remaining assumptions and risks are stated.

“Works on my machine” is not sufficient evidence of completion.

---

## 14. Final response format

After making changes, report:

### Summary

What was implemented or changed.

### Files changed

```text
Created:
- path/to/file

Modified:
- path/to/file

Deleted:
- None
```

### Verification

- Commands run.
- Results.
- Checks not run and reasons.

### Assumptions

List any assumptions used.

### Remaining risks

List unresolved requirements, risks or follow-up work.

Do not hide incomplete work.

---

## 15. Local instruction files

Read the nearest applicable instruction file before changing a specialized
area.

```text
backend/AGENTS.md
```

Contains backend, FastAPI, Python, database, migration, API and backend-testing
rules.

```text
frontend/AGENTS.md
```

Contains React, TypeScript, component, API-client, UI-state and
frontend-testing rules.

```text
backend/app/algorithms/genetic/AGENTS.md
```

Contains chromosome, fitness, hard constraint, soft constraint, selection,
crossover, mutation, seed, metric and algorithm-testing rules.

Additional local instruction files may be introduced only when a directory has
stable rules that do not belong in this root file.

---

## 16. Final principles

When choosing between guessing and asking for clarification, ask for
clarification.

When choosing between a large change and a small testable change, prefer the
small testable change.

When choosing between a high-scoring invalid timetable and a lower-scoring
valid timetable, prefer the valid timetable.

When choosing between clever code and clear code with tests, prefer clear code
with tests.
