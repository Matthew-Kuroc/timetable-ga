# Scheduling Constraints

This document defines the shared hard and soft constraints for GA, backend conflict checking and change-request approval.

## 1. Hard Constraints

Hard constraints must not be silently ignored. A high fitness score does not make a timetable valid when hard constraints are violated.

| Code | Constraint | Required data | Applies to |
| --- | --- | --- | --- |
| HC-01 | A lecturer must not teach two classes at the same time. | `lecturer_code`, `slot_code`, `weeks` | GA, conflict checker, manual change |
| HC-02 | A room must not host two classes at the same time. | `room_code`, `slot_code`, `weeks` | GA, conflict checker, manual change |
| HC-03 | Each course section must receive the required number of sessions. | `section_code`, `number_of_sessions`, generated sessions | GA |
| HC-04 | Each session must use a valid time slot. | `slot_code`, `time_slots.active` | Import validation, GA, manual change |
| HC-05 | Room type must match course-section type. | `course_type`, `room_type` | GA, conflict checker, manual change |
| HC-06 | Room capacity must be greater than or equal to `scheduling_student_count`. | `capacity`, `scheduling_student_count` | GA, conflict checker, manual change |
| HC-07 | Lecturer must not be scheduled into mandatory unavailable slots. | `lecturer_unavailable_slots` | GA, conflict checker, manual change |
| HC-08 | Room must not be scheduled into unavailable slots. | `room_unavailable_slots` | GA, conflict checker, manual change |
| HC-09 | A session must have course section, lecturer, room and time slot. | generated sessions | GA output validation |
| HC-10 | Sessions must be within allowed teaching weeks. | `weeks`, generated session week | GA, conflict checker, manual change |
| HC-11 | If a course section has multiple sessions per week, confirmed spacing rules must be applied when available. | section schedule pattern | GA, conflict checker |
| HC-12 | Change requests may be applied only after Training Department approval and must not create new hard-constraint violations. | request status, approval, conflict result | Request workflow |

## 2. Current Capacity Rule

For the draft MVP, use:

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

This is the current SRS draft decision. Keep the implementation centralized so it can be changed if the supervisor adjusts the rule.

## 3. Soft Constraints

Soft constraints affect quality and fitness but do not make a timetable invalid by themselves.

| Code | Constraint | Metric idea |
| --- | --- | --- |
| SC-01 | Prefer lecturer desired time slots. | Count sessions outside preferred slots. |
| SC-02 | Avoid too many consecutive sessions for one lecturer. | Count consecutive-session excess. |
| SC-03 | Reduce gaps between sessions in the same day. | Sum idle gaps between sessions. |
| SC-04 | Distribute teaching schedule reasonably across the week. | Penalize uneven day distribution. |
| SC-05 | Avoid night, Saturday or Sunday sessions when unnecessary. | Count undesirable slot assignments. |
| SC-06 | Prefer room capacity close to class size. | Penalize unused capacity ratio. |
| SC-07 | Avoid frequent campus changes for one lecturer. | Count campus changes between adjacent sessions. |
| SC-08 | Prefer schedule stability for sessions of the same course section. | Penalize inconsistent day/slot patterns. |
| SC-09 | Prefer fewer soft violations when all hard constraints pass. | Weighted total soft-violation score. |

## 4. Open Issues

- Exact spacing rule for multiple sessions per week is not finalized.
- Practical-class scheduling rules may require additional hard constraints.
- Exceptional teaching slots, if any, are not finalized.
- Initial soft-constraint weights still need confirmation.
- Make-up class behavior after a suspended session still needs confirmation.

