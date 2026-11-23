"""Small SQLite persistence layer for SKU-level daily sales observations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SalesObservation:
    sku: str
    date: str
    units_sold: float


class SalesStore:
    """Persist validated daily observations without requiring a database server."""

    def __init__(self, database: str | Path = "data/demandiq.db") -> None:
        self.database = str(database)
        if self.database != ":memory:":
            Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sales_observations (
                    sku TEXT NOT NULL,
                    sales_date TEXT NOT NULL,
                    units_sold REAL NOT NULL CHECK (units_sold >= 0),
                    PRIMARY KEY (sku, sales_date)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_observations(sales_date)"
            )

    def upsert(self, observation: SalesObservation) -> None:
        """Insert an observation or replace the value for the same SKU and date."""
        sku = observation.sku.strip()
        if not sku:
            raise ValueError("SKU must not be empty.")
        if observation.units_sold < 0:
            raise ValueError("Units sold must be non-negative.")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sales_observations (sku, sales_date, units_sold)
                VALUES (?, ?, ?)
                ON CONFLICT(sku, sales_date)
                DO UPDATE SET units_sold = excluded.units_sold
                """,
                (sku, observation.date, float(observation.units_sold)),
            )

    def upsert_many(self, observations: list[SalesObservation]) -> int:
        """Atomically write a batch; a validation or SQL error rolls back the batch."""
        for item in observations:
            if not item.sku.strip() or item.units_sold < 0:
                raise ValueError("Each observation needs a SKU and non-negative units.")
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO sales_observations (sku, sales_date, units_sold)
                VALUES (?, ?, ?)
                ON CONFLICT(sku, sales_date)
                DO UPDATE SET units_sold = excluded.units_sold
                """,
                [(item.sku.strip(), item.date, float(item.units_sold)) for item in observations],
            )
        return len(observations)

    def history(self, sku: str) -> list[SalesObservation]:
        """Return observations ordered oldest to newest for a single SKU."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sku, sales_date, units_sold
                FROM sales_observations
                WHERE sku = ?
                ORDER BY sales_date ASC
                """,
                (sku.strip(),),
            ).fetchall()
        return [
            SalesObservation(row["sku"], row["sales_date"], row["units_sold"])
            for row in rows
        ]

    def skus(self) -> list[str]:
        """Return distinct SKU identifiers in stable sorted order."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT sku FROM sales_observations ORDER BY sku ASC"
            ).fetchall()
        return [row["sku"] for row in rows]
