"""Tests for cli-collective, the umbrella package."""
from __future__ import annotations

import io
import re
from contextlib import redirect_stdout
from pathlib import Path

try:
    import tomllib as toml_reader
except ModuleNotFoundError:  # py<3.11
    import tomli as toml_reader

from cli_collective import cli

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"

# Minimum floors the stack is expected to declare.
EXPECTED_FLOORS = {
    "cli-wikia": "0.11.1",
    "cli-enforcement": "0.3.0",
    "cli-fleet": "0.2.0",
}


def _load_pyproject():
    with open(PYPROJECT, "rb") as f:
        return toml_reader.load(f)


def _parse_floor(dep: str):
    """Return (name, floor_string) from a 'name>=X.Y.Z' dependency spec."""
    m = re.match(r"^([A-Za-z0-9_.-]+)\s*>=\s*([0-9][0-9A-Za-z.-]*)", dep)
    assert m, f"dependency has no >= floor: {dep!r}"
    return m.group(1), m.group(2)


def _ver_tuple(v: str):
    return tuple(int(p) for p in v.split("."))


def test_version_matches_pyproject():
    data = _load_pyproject()
    assert cli.__version__ == data["project"]["version"]


def test_dependencies_have_expected_floors():
    data = _load_pyproject()
    floors = dict(_parse_floor(d) for d in data["project"]["dependencies"])
    for name, expected in EXPECTED_FLOORS.items():
        assert name in floors, f"missing dependency: {name}"
        assert _ver_tuple(floors[name]) >= _ver_tuple(expected), (
            f"{name} floor {floors[name]} is below expected {expected}"
        )


def test_main_output_mentions_all_layers():
    buf = io.StringIO()
    with redirect_stdout(buf):
        cli.main([])
    out = buf.getvalue().lower()
    for token in ("wikia", "enforcement", "fleet"):
        assert token in out, f"CLI output missing layer: {token}"
