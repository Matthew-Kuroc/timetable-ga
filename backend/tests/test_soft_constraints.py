from __future__ import annotations

import unittest
from pathlib import Path

from backend.app.algorithms.genetic.simple_ga import GeneticAlgorithmConfig, run_simple_genetic_algorithm
from backend.app.algorithms.genetic.soft_constraints import SoftConstraintWeights, score_soft_constraints
from backend.app.domain.models import ScheduleAssignment
from backend.app.importing.csv_validator import validate_sample_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class SoftConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)
        self.assertTrue(result.is_valid)
        assert result.data is not None
        self.input_data = result.data

    def test_soft_breakdown_matches_total(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(population_size=30, generations=20, seed=11),
        )

        self.assertIsNotNone(result.best_candidate)
        assert result.best_candidate is not None
        evaluation = result.best_candidate.evaluation
        self.assertAlmostEqual(evaluation.soft_cost, sum(evaluation.soft_breakdown.values()))
        self.assertIn("lecturer_preferences", evaluation.soft_breakdown)
        self.assertIn("room_capacity_waste", evaluation.soft_breakdown)

    def test_weight_configuration_changes_soft_score(self) -> None:
        assignments = (
            ScheduleAssignment("IT401_01", "F201", "TUE_1_3"),
            ScheduleAssignment("IT402_01", "B204", "MON_1_3"),
            ScheduleAssignment("IT403_01", "LAB301", "FRI_1_5"),
            ScheduleAssignment("IT404_01", "LAB401", "SAT_1_6"),
            ScheduleAssignment("IT405_01", "A303", "MON_10_12"),
        )

        default_score = score_soft_constraints(self.input_data, assignments, SoftConstraintWeights())
        zero_preference_score = score_soft_constraints(
            self.input_data,
            assignments,
            SoftConstraintWeights(lecturer_preferences=0),
        )

        self.assertGreater(default_score["lecturer_preferences"], zero_preference_score["lecturer_preferences"])

    def test_weekend_has_configurable_default_avoidance_without_preference(self) -> None:
        assignments = (
            ScheduleAssignment("IT404_01", "LAB401", "SAT_1_6"),
        )

        score = score_soft_constraints(
            self.input_data,
            assignments,
            SoftConstraintWeights(
                lecturer_preferences=0,
                room_capacity_waste=0,
                large_room_small_class=0,
                schedule_gaps=0,
                scattered_days=0,
                consecutive_sessions=0,
            ),
        )

        self.assertGreater(score["evening_weekend_avoidance"], 0)

    def test_invalid_soft_weight_is_reported_by_ga_config(self) -> None:
        result = run_simple_genetic_algorithm(
            self.input_data,
            GeneticAlgorithmConfig(
                population_size=10,
                generations=10,
                seed=1,
                soft_weights=SoftConstraintWeights(room_capacity_waste=-1),
            ),
        )

        self.assertEqual(result.status, "FAILED")
        self.assertEqual(result.stop_reason, "INVALID_CONFIGURATION")


if __name__ == "__main__":
    unittest.main()
