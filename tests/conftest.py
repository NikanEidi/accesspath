"""Shared pytest fixtures -- built once, reused across tests, not rebuilt per test."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from src.data.synthetic_city import (
    build_old_town,
    build_riverside_district,
    build_university_quarter,
    build_industrial_row,
    build_construction_zone,
    build_dead_end_district,
    build_stairs_only_zone,
    build_disconnected_island,
    build_clearwell,
)


@pytest.fixture(scope="session")
def old_town():
    return build_old_town()


@pytest.fixture(scope="session")
def riverside_district():
    return build_riverside_district()


@pytest.fixture(scope="session")
def university_quarter():
    return build_university_quarter()


@pytest.fixture(scope="session")
def industrial_row():
    return build_industrial_row()


@pytest.fixture(scope="session")
def construction_zone():
    return build_construction_zone()


@pytest.fixture(scope="session")
def dead_end_district():
    return build_dead_end_district()


@pytest.fixture(scope="session")
def stairs_only_zone():
    return build_stairs_only_zone()


@pytest.fixture(scope="session")
def disconnected_island():
    return build_disconnected_island()


@pytest.fixture(scope="session")
def clearwell():
    return build_clearwell()
