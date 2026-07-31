from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from backend.app.algorithms.genetic.simple_ga import (
    GeneticAlgorithmConfig,
    run_simple_genetic_algorithm,
)
from backend.app.importing.csv_validator import validate_sample_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class SimpleGeneticAlgorithmTests(unittest.TestCase):
    def setUp(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)
        self.assertTrue(result.is_valid)
        assert result.data is not None
        self.input_data = result.data

    def test_finds_valid_candidate_for_small_sample(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(population_size=80, generations=200, seed=42),
        )

        self.assertEqual(result.status, "COMPLETED")
        self.assertIsNotNone(result.best_candidate)
        assert result.best_candidate is not None
        self.assertEqual(result.best_candidate.evaluation.hard_violation_count, 0)
        self.assertEqual(len(result.best_candidate.assignments), len(self.input_data.course_sections))

    def test_fixed_seed_is_reproducible(self) -> None:
        config = GeneticAlgorithmConfig(population_size=40, generations=100, seed=7)

        first = run_simple_genetic_algorithm(self.input_data, config)
        second = run_simple_genetic_algorithm(self.input_data, config)

        self.assertEqual(first.best_candidate, second.best_candidate)

    def test_invalid_configuration_is_reported(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(population_size=0, generations=10, seed=1),
        )

        self.assertEqual(result.status, "FAILED")
        self.assertEqual(result.stop_reason, "INVALID_CONFIGURATION")
        self.assertTrue(result.diagnostics)

    def test_no_feasible_assignment_domain_is_reported(self) -> None:
        rooms = {
            room_code: replace(room, available=False)
            for room_code, room in self.input_data.rooms.items()
            if room.room_type == "SPECIALIZED_LAB"
        }
        input_data = replace(
            self.input_data,
            rooms={
                **self.input_data.rooms,
                **rooms,
            },
        )

        result = run_simple_genetic_algorithm(
            input_data,
            GeneticAlgorithmConfig(population_size=10, generations=10, seed=1),
        )

        self.assertEqual(result.status, "FAILED")
        self.assertEqual(result.stop_reason, "NO_FEASIBLE_ASSIGNMENT_DOMAIN")
        self.assertIn("IT404_01", result.diagnostics[0])


if __name__ == "__main__":
    unittest.main()
