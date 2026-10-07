"""Small SQLite repository: parameterized SQL, explicit transactions, no global connection."""

import asyncio
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    async def all(self, sql, parameters=()):
        def read():
            with self.connection() as connection:
                return [
                    dict(row) for row in connection.execute(sql, parameters).fetchall()
                ]

        return await asyncio.to_thread(read)

    async def one(self, sql, parameters=()):
        rows = await self.all(sql, parameters)
        return rows[0] if rows else None

    async def execute(self, sql, parameters=()):
        def run():
            with self.connection() as connection:
                cursor = connection.execute(sql, parameters)
                return cursor.lastrowid

        return await asyncio.to_thread(run)
