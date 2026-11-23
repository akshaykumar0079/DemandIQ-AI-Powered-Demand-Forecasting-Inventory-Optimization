from __future__ import annotations

import pytest

from demandiq.data.sqlite_store import SalesObservation, SalesStore


def test_upsert_and_history_are_ordered(tmp_path):
    store = SalesStore(tmp_path / "sales.db")
    store.upsert(SalesObservation("SKU-2", "2026-01-02", 12))
    store.upsert(SalesObservation("SKU-2", "2026-01-01", 8))
    store.upsert(SalesObservation("SKU-2", "2026-01-02", 15))

    assert store.history("SKU-2") == [
        SalesObservation("SKU-2", "2026-01-01", 8.0),
        SalesObservation("SKU-2", "2026-01-02", 15.0),
    ]


def test_batch_upsert_and_sku_listing(tmp_path):
    store = SalesStore(tmp_path / "sales.db")
    count = store.upsert_many(
        [
            SalesObservation("B-2", "2026-01-01", 4),
            SalesObservation("A-1", "2026-01-01", 9),
        ]
    )

    assert count == 2
    assert store.skus() == ["A-1", "B-2"]


def test_rejects_empty_sku_and_negative_units(tmp_path):
    store = SalesStore(tmp_path / "sales.db")

    with pytest.raises(ValueError, match="SKU"):
        store.upsert(SalesObservation("  ", "2026-01-01", 2))
    with pytest.raises(ValueError, match="non-negative"):
        store.upsert(SalesObservation("A-1", "2026-01-01", -1))


def test_invalid_batch_does_not_write_partial_data(tmp_path):
    store = SalesStore(tmp_path / "sales.db")

    with pytest.raises(ValueError):
        store.upsert_many(
            [
                SalesObservation("A-1", "2026-01-01", 2),
                SalesObservation("", "2026-01-02", 3),
            ]
        )

    assert store.skus() == []
