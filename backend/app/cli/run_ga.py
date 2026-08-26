from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.app.algorithms.genetic.simple_ga import (
    GeneticAlgorithmConfig,
    run_simple_genetic_algorithm,
)
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.scheduling.calendar_expansion import expand_base_assignments_to_occurrences


def main() -> int:
    _configure_utf8_output()
    parser = argparse.ArgumentParser(description="Run GA v0.1 on a CSV sample dataset.")
    parser.add_argument(
        "--data-dir",
        default="data/samples/small",
        help="Folder containing CSV input files.",
    )
    parser.add_argument("--population-size", type=int, default=80)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--crossover-rate", type=float, default=0.8)
    parser.add_argument("--mutation-rate", type=float, default=0.1)
    parser.add_argument("--elite-count", type=int, default=2)
    parser.add_argument("--tournament-size", type=int, default=3)
    parser.add_argument("--time-limit-seconds", type=float, default=None)
    parser.add_argument(
        "--show-occurrences",
        action="store_true",
        help="Expand the base timetable by academic calendar and show dated occurrences.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    validation_result = validate_sample_dataset(data_dir)
    if not validation_result.is_valid:
        print("CSV validation failed")
        for error in validation_result.errors:
            row = "" if error.row is None else f"row={error.row} "
            column = "" if error.column is None else f"column={error.column} "
            print(f"- file={error.file} {row}{column}value={error.value} reason={error.reason}")
        return 1

    assert validation_result.data is not None
    result = run_simple_genetic_algorithm(
        validation_result.data,
        GeneticAlgorithmConfig(
            population_size=args.population_size,
            generations=args.generations,
            seed=args.seed,
            crossover_rate=args.crossover_rate,
            mutation_rate=args.mutation_rate,
            elite_count=args.elite_count,
        tournament_size=args.tournament_size,
        time_limit_seconds=args.time_limit_seconds,
        ),
    )

    print(f"status={result.status}")
    print(f"stop_reason={result.stop_reason}")
    print(f"generation_count={result.generation_count}")
    print(f"seed={result.seed}")
    print(f"execution_time_seconds={result.execution_time_seconds:.4f}")

    if result.diagnostics:
        print("diagnostics:")
        for diagnostic in result.diagnostics:
            print(f"- {diagnostic}")

    if result.best_candidate is None:
        return 1

    evaluation = result.best_candidate.evaluation
    print(f"hard_violation_count={evaluation.hard_violation_count}")
    print(f"soft_cost={evaluation.soft_cost:.2f}")
    print(f"total_cost={evaluation.total_cost:.2f}")
    print("soft_breakdown:")
    for key, value in sorted(evaluation.soft_breakdown.items()):
        print(f"- {key}={value:.2f}")
    print("assignments:")
    for assignment in sorted(result.best_candidate.assignments, key=lambda item: item.section_code):
        section = validation_result.data.course_sections[assignment.section_code]
        slot = validation_result.data.time_slots[assignment.slot_code]
        room = validation_result.data.rooms[assignment.room_code]
        print(
            f"- {assignment.section_code} | {section.course_name} | "
            f"GV={section.lecturer_code} | room={room.room_code} | "
            f"day={slot.day_of_week} | periods={slot.start_period}-{slot.end_period}"
        )

    if evaluation.hard_violations:
        print("hard_violations:")
        for violation in evaluation.hard_violations:
            print(f"- {violation.code}: {violation.message}")

    if args.show_occurrences:
        expansion = expand_base_assignments_to_occurrences(
            validation_result.data,
            tuple(result.best_candidate.assignments),
        )
        print("occurrences:")
        for occurrence in sorted(expansion.occurrences, key=lambda item: (item.date, item.section_code)):
            print(
                f"- {occurrence.date.isoformat()} | week={occurrence.academic_week} | "
                f"{occurrence.section_code} | room={occurrence.room_code} | slot={occurrence.slot_code} | "
                f"status={occurrence.status}"
            )
        if expansion.skipped_holiday_sessions:
            print("skipped_holiday_sessions:")
            for skipped in sorted(expansion.skipped_holiday_sessions, key=lambda item: (item.date, item.section_code)):
                print(
                    f"- {skipped.date.isoformat()} | week={skipped.academic_week} | "
                    f"{skipped.section_code} | holiday={skipped.holiday_name} | normal occurrence not generated"
                )

    return 0


def _configure_utf8_output() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
