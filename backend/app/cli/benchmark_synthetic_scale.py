from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from backend.app.algorithms.genetic.simple_ga import GeneticAlgorithmConfig, run_simple_genetic_algorithm
from backend.app.importing.csv_validator import validate_sample_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and benchmark a synthetic timetable dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--population-size", type=int, default=80)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--time-limit-seconds", type=float, default=None)
    args = parser.parse_args()
    validation = validate_sample_dataset(args.dataset)
    if not validation.is_valid or validation.data is None:
        print(json.dumps({"valid": False, "errors": [error.__dict__ for error in validation.errors]}, ensure_ascii=False))
        return 2
    started = time.perf_counter()
    result = run_simple_genetic_algorithm(validation.data, GeneticAlgorithmConfig(population_size=args.population_size, generations=args.generations, seed=args.seed, time_limit_seconds=args.time_limit_seconds))
    elapsed = time.perf_counter() - started
    print(json.dumps({"valid": True, "status": result.status, "stop_reason": result.stop_reason, "runtime_seconds": round(elapsed, 3), "execution_time_seconds": round(result.execution_time_seconds, 3), "generation_count": result.generation_count, "gene_count": len(result.best_candidate.assignments) if result.best_candidate else 0, "hard_violations": result.best_candidate.evaluation.hard_violation_count if result.best_candidate else None, "soft_cost": result.best_candidate.evaluation.soft_cost if result.best_candidate else None, "occurrence_expansion": "run separately after a successful base timetable"}, ensure_ascii=False))
    return 0 if result.best_candidate is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
