# Scheduling Constraints

This document defines shared constraints for GA generation, backend conflict checking, manual schedule edits and request approval.

## 1. Hard Constraints

Hard constraints must not be silently ignored. A timetable with hard violations is invalid even if its soft score is good.

| Code | Constraint | Required data | Applies to |
| --- | --- | --- | --- |
| HC-01 | A lecturer must not teach overlapping classes. | section lecturer, day, period range | GA, manual edit, request approval |
| HC-02 | A room must not host overlapping classes. | room, day, period range | GA, manual edit, request approval |
| HC-03 | Each declared `(section_code, meeting_number)` must receive exactly one base weekly assignment. | section meetings, assignments | GA output validation |
| HC-04 | Selected time slot must exist and be active. | `slot_code`, `time_slots.active` | Import, GA, manual edit |
| HC-05 | Time slot must support course type and session duration. | `course_type`, `periods_per_session`, slot range, `supports_course_types` | Import, GA, manual edit |
| HC-06 | Room type must satisfy `required_room_type`. | `required_room_type`, `room_type` | GA, manual edit |
| HC-07 | Room capacity must satisfy `scheduling_student_count`. | `capacity`, `scheduling_student_count` | GA, manual edit |
| HC-08 | Room must be available and not unavailable for the selected slot. | `rooms.available`, `room_unavailable_slots` | GA, manual edit |
| HC-09 | Officially confirmed lecturer restrictions must not be violated. Ordinary lecturer preferences are not hard constraints. | `lecturer_time_preferences.mandatory` | GA, manual edit |
| HC-10 | Required assignment references must exist. | section, room, slot references | GA output validation |
| HC-11 | Schedule segments must not create contradictory schedules for the same occurrence. | segment effective ranges | Manual segment edit |
| HC-12 | Lecturer requests may be applied only after Training Office processing and conflict validation. | request status, reviewer, conflict result | Request workflow |
| HC-13 | A normal dated occurrence must not be generated on a holiday or non-teaching day. | academic calendar date, base assignment | Calendar expansion |
| HC-14 | A make-up session must use a valid configured teaching date no later than academic week 18. Week 19 and later are outside the current make-up window. | academic calendar, original missing occurrence, room, slot | Manual make-up edit |
| HC-15 | After official publication, a whole-recurring day/time change is locked. A long-term room-only segment must preserve day and slot and pass room validation. | publication status, segment, room, audit reason | Manual segment edit, request workflow |

Overlap is based on actual period ranges:

```text
start_a <= end_b
and
start_b <= end_a
```

Periods `1-5` and `2-6` overlap.

## 2. Course Type And Slot Rules

| Course type | Session length | Valid ranges |
| --- | --- | --- |
| `THEORY` | 3 periods | `1-3`, `4-6`, `7-9`, `10-12`, `13-15` |
| `PRACTICE` | 5 or 6 total weekly periods | One configured 5/6-period meeting, or declared components such as `3+2`/`3+3` using configured component slots. |
| `INTEGRATED` | 5 or 6 total weekly periods | One configured 5/6-period meeting, or declared components such as `3+2`/`3+3` using configured component slots. |

Do not infer required room type only from `course_type`; use explicit `required_room_type`.

An explicitly declared `PRACTICE` or `INTEGRATED` section may have two weekly
meetings. `periods_per_session` describes meeting 1 and
`second_session_periods` meeting 2; normalization derives stable meeting
numbers. The meetings remain the same course type, have no minimum day gap and
may occur on consecutive days. The GA must not infer or create the split.

## 3. Capacity Rule

```text
scheduling_student_count =
  approved_max_students
  else initial_registration_limit
  else expected_students
```

Then require:

```text
room.capacity >= scheduling_student_count
```

## 4. Soft Constraints

Soft constraints affect quality and fitness but do not invalidate a timetable.

| Code | Constraint | Metric idea |
| --- | --- | --- |
| SC-01 | Prefer lecturer preferred days and slots. | Count or weight sessions outside preferences. |
| SC-02 | Avoid lecturer undesired days and slots, including non-mandatory lecturer time-preference rows. | Count or weight undesired assignments. |
| SC-03 | Reduce long gaps in a lecturer's teaching day. | Sum idle period gaps. |
| SC-04 | Avoid unnecessarily scattered teaching days. | Penalize excessive teaching days when configured. |
| SC-05 | Prefer room capacity close to class size. | Penalize unused capacity. |
| SC-06 | Preserve large halls when suitable standard rooms remain available. | Configurable large-room waste penalty. |
| SC-07 | Keep stable regular schedules. | Penalize unnecessary changes between runs or edits. |
| SC-08 | Prefer weekday and daytime assignments when no lecturer-specific preference applies. | Add configurable cost for evening, Saturday or Sunday assignments; waive the matching default cost when the lecturer explicitly prefers that day or slot. |

Saturday, Sunday, and evening slots are valid options. Their project-wide
avoidance costs are soft, configurable, recorded with each GA run, and never
turn an assignment into a hard-constraint violation. A lecturer who explicitly
prefers the relevant day or slot does not receive that matching default cost.

Target GA scoring groups:

| Breakdown key | Related constraints | Default weight | Notes |
| --- | --- | ---: | --- |
| `lecturer_preferences` | SC-01, SC-02 | 10.0 | Penalizes assignments outside declared preferred days/slots, assignments on undesired days/slots, and non-mandatory lecturer time-preference rows. |
| `room_capacity_waste` | SC-05 | 1.0 | Penalizes unused room capacity while keeping insufficient capacity as a hard violation. |
| `large_room_small_class` | SC-06 | 25.0 | Penalizes assigning a `LARGE_HALL` to a class below the large-class threshold. The assignment remains valid. |
| `schedule_gaps` | SC-03 | 4.0 | Sums idle period gaps between the same lecturer's sessions on the same day. Consecutive sessions do not add cost. |
| `scattered_days` | SC-04 | 8.0 | Penalizes days above `lecturer.max_days_per_week` when that preference is configured. |
| `consecutive_sessions` | SC-04 | 6.0 | Penalizes runs above `lecturer.max_consecutive_sessions` when that preference is configured. |
| `evening_weekend_avoidance` | SC-08 | 5.0 | Adds cost for an evening, Saturday or Sunday allocation only when the matching lecturer preference does not explicitly allow it. |

The current evaluator uses lexicographic ranking:

```text
1. Fewer hard-constraint violations.
2. Lower total soft cost.
3. Stable assignment order as a deterministic tie-breaker.
```

Therefore, an invalid timetable must not outrank a valid timetable only because its soft score is lower.

## 5. Open Issues

- The accepted weights are an experiment baseline, not a claim of global
  optimality; each run must store its configured snapshot.
