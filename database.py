"""Database connections: local SQLite or verified-TLS Supabase PostgreSQL."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent
SQLITE_PATH = Path(os.environ.get('HOPETECH_DB', ROOT / 'data' / 'hopetech.sqlite3'))
INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg.IntegrityError)

class PostgresConnection:
    def __init__(self, connection): self.connection = connection
    def execute(self, query, parameters=None):
        return self.connection.execute(query.replace('?', '%s'), parameters)

@contextmanager
def connect():
    url = os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')
    if url:
        options = {'sslmode': 'verify-full', 'sslrootcert': 'system'}
        # Explicit, loopback-only option for integration tests/local development.
        if os.environ.get('HOPETECH_LOCAL_POSTGRES') == '1' and not os.environ.get('VERCEL'):
            if urlsplit(url).hostname not in ('127.0.0.1', 'localhost'):
                raise RuntimeError('Local PostgreSQL mode requires a loopback host.')
            options = {'sslmode': 'disable'}
        with psycopg.connect(url, connect_timeout=10, prepare_threshold=None,
                             row_factory=dict_row, **options) as connection:
            connection.execute('SET LOCAL search_path TO hopetech, public')
            connection.execute("SET LOCAL statement_timeout = '10s'")
            yield PostgresConnection(connection)
        return
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        raise RuntimeError('The hosted database is not configured; SQLite fallback is disabled.')
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(SQLITE_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def initialize():
    """Explicit setup only; never run schema changes on a web request."""
    url = os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')
    if url:
        with connect() as connection:
            # No interpolation or application data in this trusted schema file.
            connection.connection.execute((ROOT / 'database' / 'schema.sql').read_text(), prepare=False)
        return
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        raise RuntimeError('Set the hosted database URL before setup.')
    with connect() as connection:
        connection.executescript('''
CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,csrf TEXT NOT NULL,expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL,phone TEXT NOT NULL,course TEXT NOT NULL,schedule TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Pending',notes TEXT NOT NULL DEFAULT '',created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(email,course));
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL,message TEXT NOT NULL,created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY,count INTEGER NOT NULL,expires INTEGER NOT NULL);
''')
    SQLITE_PATH.chmod(0o600)
