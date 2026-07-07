"""
The tests in this file test the CLI wrapper (shadowfinder.cli).
"""

import inspect

import pytest

from shadowfinder.cli import ShadowFinderCli

# The timezone grid file that ships with the package and is produced by
# `generate_timezone_grid`. Commands that read a cached grid must default to
# this exact name, otherwise the lookup misses and the grid is regenerated
# from scratch on every run (see quick_find's FileNotFoundError fallback).
EXPECTED_GRID = "timezone_grid.json"


@pytest.mark.parametrize("command", ["find", "find_sun", "generate_timezone_grid"])
def test_cli_grid_default_is_consistent(command):
    """Every CLI command that takes a `grid` argument must default to the same
    packaged grid filename. A mismatched default silently defeats grid caching."""
    # GIVEN
    signature = inspect.signature(getattr(ShadowFinderCli, command))

    # WHEN
    grid_param = signature.parameters["grid"]

    # THEN
    assert grid_param.default == EXPECTED_GRID
