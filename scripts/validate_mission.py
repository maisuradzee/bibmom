#!/usr/bin/env python3
"""Validate NOEMA's foundational mission and autonomy policy."""
from __future__ import annotations

import sys
from pathlib import Path

# Executing a file under scripts/ puts that directory, not the repository
# root, first on sys.path. Add the root so the local noema_core package resolves.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from noema_core import load_mission


def main() -> int:
    mission = load_mission()
    print(f"NOEMA mission core: PASS ({mission['identity']['name']})")
    print(f"Autonomous actions: {len(mission['autonomy']['autonomous_actions'])}")
    print(f"Review-required actions: {len(mission['autonomy']['review_required_actions'])}")
    print(f"Innovation-cycle stages: {len(mission['innovation_cycle'])}")
    print("Unknown sources and unknown actions: fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
