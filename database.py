from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

import pandas as pd

from config import (
    BROKER_SERVICE_FEE,
    CUSTOMS_COLLECTION,
    DATABASE_PATH,
    SBKTS_EPTS_FEE,
)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_number TEXT NOT NULL UNIQUE,
                quote_date TEXT NOT NULL,
                valid_until TEXT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                production_year TEXT,
                engine TEXT,
                source TEXT,
                original_price_usd REAL,
                vat_amount_usd REAL,
                price_with_vat_usd REAL,
                customs_collection_kzt REAL,
                sbkts_epts_fee_kzt REAL,
                broker_service_fee_kzt REAL,
                status TEXT NOT NULL DEFAULT '已报价',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_quote_phone ON quotations(customer_phone)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_quote_created ON quotations(created_at)"
        )
        connection.commit()


def save_quotation(data: dict[str, Any]) -> bool:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO quotations (
                    quote_number,
                    quote_date,
                    valid_until,
                    customer_name,
                    customer_phone,
                    brand,
                    model,
                    production_year,
                    engine,
                    source,
                    original_price_usd,
                    vat_amount_usd,
                    price_with_vat_usd,
                    customs_collection_kzt,
                    sbkts_epts_fee_kzt,
                    broker_service_fee_kzt,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["quote_number"],
                    data["quote_date"],
                    data["valid_until"],
                    data["customer_name"],
                    data["customer_phone"],
                    data["brand"],
                    data["model"],
                    data["production_year"],
                    data["engine"],
                    data["source"],
                    data["original_price_usd"],
                    data["vat_amount_usd"],
                    data["price_with_vat_usd"],
                    CUSTOMS_COLLECTION,
                    SBKTS_EPTS_FEE,
                    BROKER_SERVICE_FEE,
                    created_at,
                ),
            )
            connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def count_quotations() -> int:
    with get_connection() as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM quotations").fetchone()
    return int(row["total"])


def count_today() -> int:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM quotations
            WHERE date(created_at) = date('now', 'localtime')
            """
        ).fetchone()
    return int(row["total"])


def count_this_month() -> int:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM quotations
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
            """
        ).fetchone()
    return int(row["total"])


def fetch_quotations(search_text: str = "") -> pd.DataFrame:
    query = """
        SELECT
            id,
            quote_number,
            quote_date,
            valid_until,
            customer_name,
            customer_phone,
            brand,
            model,
            production_year,
            engine,
            source,
            original_price_usd,
            vat_amount_usd,
            price_with_vat_usd,
            status,
            notes,
            created_at
        FROM quotations
    """
    params: tuple[Any, ...] = ()

    if search_text.strip():
        like = f"%{search_text.strip()}%"
        query += """
            WHERE customer_name LIKE ?
               OR customer_phone LIKE ?
               OR brand LIKE ?
               OR model LIKE ?
               OR quote_number LIKE ?
        """
        params = (like, like, like, like, like)

    query += " ORDER BY id DESC"

    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=params)


def update_quotation_status(record_id: int, status: str, notes: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE quotations
            SET status = ?, notes = ?
            WHERE id = ?
            """,
            (status, notes, record_id),
        )
        connection.commit()


def delete_quotation(record_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM quotations WHERE id = ?", (record_id,))
        connection.commit()
