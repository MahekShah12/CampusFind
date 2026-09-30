"""Tiny SQLite migration so an already-existing campusfind.db keeps working
after new columns are added (create_all never alters existing tables)."""
from sqlalchemy import inspect, text

NEW_COLUMNS = {
    "users": [("phone", "VARCHAR DEFAULT ''")],
    "items": [("user_id", "INTEGER")],
    "claims": [
        ("reviewed_by", "INTEGER"),
        ("reviewed_at", "DATETIME"),
        ("handover_location", "VARCHAR DEFAULT ''"),
        ("handover_status", "VARCHAR NOT NULL DEFAULT 'NOT_ASSIGNED'"),
    ],
}


def run_light_migrations(engine) -> None:
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in NEW_COLUMNS.items():
            if not insp.has_table(table):
                continue
            existing = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
