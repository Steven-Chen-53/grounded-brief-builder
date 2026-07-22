#!/usr/bin/env python3
"""Run the dependency-free automated test suite."""

from __future__ import annotations

import unittest
from pathlib import Path


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
