"""Small DB-API adapter shared by SQLite demos and MySQL installations."""

from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3


class Database:
    def __init__(self, connection, backend="sqlite"):
        self.connection = connection
        self.backend = backend

    @classmethod
    def sqlite(cls, path=":memory:"):
        connection = sqlite3.connect(path)
        connection.execute("PRAGMA foreign_keys = ON")
        return cls(connection)

    @classmethod
    def mysql(cls):
        try:
            import mysql.connector
        except ImportError as exc:
            raise RuntimeError("Install requirements.txt before using MySQL.") from exc
        password = os.environ.get("GRADEBOOK_DB_PASSWORD")
        if password is None:
            raise ValueError("Set GRADEBOOK_DB_PASSWORD before connecting to MySQL.")
        connection = mysql.connector.connect(
            host=os.environ.get("GRADEBOOK_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("GRADEBOOK_DB_PORT", "3306")),
            user=os.environ.get("GRADEBOOK_DB_USER", "gradebook"),
            password=password,
            database=os.environ.get("GRADEBOOK_DB_NAME", "gradebook"),
            autocommit=True,
        )
        return cls(connection, "mysql")

    def execute(self, sql, parameters=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql.replace("?", "%s") if self.backend == "mysql" else sql, parameters)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return cursor.lastrowid
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        try:
            if self.backend == "mysql":
                self.connection.start_transaction()
            else:
                self.connection.execute("BEGIN")
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def initialize(self):
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        if self.backend == "mysql":
            schema = schema.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER PRIMARY KEY AUTO_INCREMENT")
        for statement in schema.split(";"):
            if statement.strip():
                self.execute(statement)
        self.connection.commit()

    def close(self):
        self.connection.close()
