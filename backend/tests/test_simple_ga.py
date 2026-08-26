from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from backend.app.algorithms.genetic.simple_ga import (
    GeneticAlgorithmConfig,
    run_simple_genetic_algorithm,
)
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.domain.models import TimeSlot


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

    def test_practice_two_meetings_use_two_stable_genes(self) -> None:
        section = replace(self.input_data.course_sections["IT403_01"], weekly_sessions=2, periods_per_session=3, second_session_periods=2)
        input_data = replace(
            self.input_data,
            course_sections={**self.input_data.course_sections, section.section_code: section},
            time_slots={
                **self.input_data.time_slots,
                "PRACTICE_MON_1_3": TimeSlot("PRACTICE_MON_1_3", 2, 1, 3, ("PRACTICE",), True),
                "PRACTICE_MON_4_5": TimeSlot("PRACTICE_MON_4_5", 2, 4, 5, ("PRACTICE",), True),
            },
        )

        result = run_simple_genetic_algorithm(input_data, GeneticAlgorithmConfig(population_size=30, generations=40, seed=42))

        self.assertIsNotNone(result.best_candidate)
        assert result.best_candidate is not None
        self.assertEqual(result.best_candidate.evaluation.hard_violation_count, 0)
        meetings = [item for item in result.best_candidate.assignments if item.section_code == "IT403_01"]
        self.assertEqual({item.meeting_number for item in meetings}, {1, 2})

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

    def test_time_limit_preserves_best_so_far(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(population_size=20, generations=200, seed=42, time_limit_seconds=0.0001),
        )
        self.assertEqual(result.status, "STOPPED")
        self.assertEqual(result.stop_reason, "TIME_LIMIT")
        self.assertIsNotNone(result.best_candidate)

    def test_cancellation_callback_stops_after_first_generation(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(population_size=20, generations=200, seed=42, cancellation_callback=lambda: True),
        )
        self.assertEqual(result.status, "STOPPED")
        self.assertEqual(result.stop_reason, "CANCELLED")
        self.assertIsNotNone(result.best_candidate)


if __name__ == "__main__":
    unittest.main()
