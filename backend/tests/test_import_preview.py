from __future__ import annotations

import unittest
from pathlib import Path

from backend.app.importing.import_preview import REQUIRED_DATASET_FILES, preview_and_validate_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class ImportPreviewTests(unittest.TestCase):
    def test_preview_contains_headers_sample_rows_and_validation_result(self) -> None:
        result = preview_and_validate_dataset(SAMPLE_DIR, sample_size=2)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.files), len(REQUIRED_DATASET_FILES))
        course_sections = next(file for file in result.files if file.file == "course_sections.csv")
        self.assertIn("section_code", course_sections.headers)
        self.assertLessEqual(len(course_sections.sample_rows), 2)
        self.assertGreater(course_sections.row_count, 0)


if __name__ == "__main__":
    unittest.main()
