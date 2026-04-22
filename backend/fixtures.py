from __future__ import annotations

import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).resolve().parent / "data" / "neurobotics_fixture.json"


def load_fixture_dataset() -> list[dict]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)

