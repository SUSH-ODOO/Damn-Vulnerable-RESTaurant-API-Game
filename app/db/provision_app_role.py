"""Idempotently provision the unprivileged runtime role used by the web service.

Must be executed with the bootstrap (administrative) credentials, after the
migrations have run. It is invoked by the one-shot ``migrate`` service only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2  # noqa: E402
from config import settings  # noqa: E402
from psycopg2 import sql  # noqa: E402

APP_TABLE_PRIVILEGES = "SELECT, INSERT, UPDATE, DELETE"


def provision():
    if not settings.POSTGRES_USER or not settings.POSTGRES_PASSWORD:
        raise RuntimeError("POSTGRES_USER and POSTGRES_PASSWORD must be set")
    if settings.APP_DB_USER == settings.POSTGRES_USER:
        raise RuntimeError("APP_DB_USER must differ from the bootstrap user")

    conn = psycopg2.connect(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )
    conn.autocommit = True
    role = sql.Identifier(settings.APP_DB_USER)
    database = sql.Identifier(settings.POSTGRES_DB)
    password = sql.Literal(settings.APP_DB_PASSWORD)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s", (settings.APP_DB_USER,)
        )
        verb = "ALTER" if cur.fetchone() else "CREATE"
        cur.execute(
            sql.SQL(
                "{} ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                "NOREPLICATION NOBYPASSRLS PASSWORD {}"
            ).format(sql.SQL(verb), role, password)
        )

        cur.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(database, role))
        cur.execute(sql.SQL("REVOKE CREATE ON SCHEMA public FROM {}").format(role))
        cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(role))
        cur.execute(
            sql.SQL(
                "GRANT " + APP_TABLE_PRIVILEGES + " ON ALL TABLES IN SCHEMA public TO {}"
            ).format(role)
        )
        cur.execute(
            sql.SQL(
                "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
            ).format(role)
        )
        # Tables/sequences created by future migrations (run as the bootstrap user).
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT "
                + APP_TABLE_PRIVILEGES
                + " ON TABLES TO {}"
            ).format(role)
        )
        cur.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT "
                "ON SEQUENCES TO {}"
            ).format(role)
        )
        # The migration bookkeeping table is not needed at runtime.
        cur.execute("SELECT to_regclass('public.alembic_version')")
        if cur.fetchone()[0]:
            cur.execute(
                sql.SQL("REVOKE ALL ON TABLE public.alembic_version FROM {}").format(
                    role
                )
            )
    conn.close()


if __name__ == "__main__":
    provision()
