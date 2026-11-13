from __future__ import annotations

import logging
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def run_additive_migrations(engine: Engine) -> None:
    """Safely applies additive schema changes for SQLite / PostgreSQL without vendor-specific PRAGMAs."""
    columns_to_add = [
        ("experiments", "pack_id", "VARCHAR(100)"),
        ("runs", "taxonomy_counts", "JSON"),
        ("runs", "remediation_hints", "JSON"),
        ("trials", "taxonomy_category", "VARCHAR(50)"),
        ("trials", "prompt_tokens", "INTEGER DEFAULT 0"),
        ("trials", "completion_tokens", "INTEGER DEFAULT 0"),
        ("trials", "cost_usd", "FLOAT DEFAULT 0.0"),
    ]

    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        with engine.connect() as conn:
            for table, col, col_type in columns_to_add:
                if table not in existing_tables:
                    continue

                try:
                    existing_cols = {c["name"] for c in inspector.get_columns(table)}
                    if col not in existing_cols:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};"))
                        conn.commit()
                        logger.info(f"Added column {col} to {table}")
                except Exception as e:
                    logger.debug(f"Migration note for {table}.{col}: {e}")
    except Exception as e:
        logger.warning(f"Could not inspect schema for additive migrations: {e}")
