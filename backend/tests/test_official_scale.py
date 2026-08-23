from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from backend.app.algorithms.genetic.simple_ga import GeneticAlgorithmConfig, run_simple_genetic_algorithm
from backend.app.importing.csv_validator import validate_sample_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_official_fixture_has_target_scale() -> None:
    result = validate_sample_dataset(REPO_ROOT / "data" / "samples" / "official")
    assert result.is_valid
    assert result.data is not None
    assert len(result.data.lecturers) == 20
    assert 100 <= len(result.data.course_sections) <= 200


def test_official_fixture_ga_benchmark_when_enabled() -> None:
    if os.getenv("RUN_SCALE_BENCHMARK") != "1":
        pytest.skip("Bật RUN_SCALE_BENCHMARK=1 để chạy benchmark GA quy mô 120 lớp.")
    result = validate_sample_dataset(REPO_ROOT / "data" / "samples" / "official")
    assert result.data is not None
    started = time.perf_counter()
    ga_result = run_simple_genetic_algorithm(
        result.data,
        GeneticAlgorithmConfig(population_size=20, generations=20, seed=42),
    )
    elapsed = time.perf_counter() - started
    assert ga_result.best_candidate is not None
    assert ga_result.best_candidate.evaluation.hard_violation_count == 0
    print(f"official_scale_seconds={elapsed:.3f} hard_violations=0 generations={ga_result.generation_count}")
