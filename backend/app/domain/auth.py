from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    TRAINING_OFFICE = "TRAINING_OFFICE"
    LECTURER = "LECTURER"

