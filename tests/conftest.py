from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine

from cronos.persistence.schema import metadata


@pytest.fixture
def engine() -> Generator[Engine, Any, None]:
    e = create_engine("sqlite:///:memory:", echo=True)
    metadata.create_all(e)
    yield e
    metadata.drop_all(e)
    e.dispose()
