"""Centralized app configuration.

Avoids SECRET_KEY mismatches across modules by importing from a single place.
Values are sourced from environment variables at process start.
"""

from __future__ import annotations

import os

# Security and auth settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
