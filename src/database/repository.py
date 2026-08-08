"""
Database Repository Module for E-Commerce Sales Intelligence.
Provides helper methods to execute raw SQL or ORM analytical queries against database.
"""

import pandas as pd
from sqlalchemy import text
from .connection import get_db_engine

class DatabaseRepository:
    """
    Executes business SQL queries against SQLite/PostgreSQL database.
    """

    def __init__(self, db_path: str = "data/ecommerce.db"):
        self.engine = get_db_engine(db_path)

    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """Executes a SQL query string and returns a Pandas DataFrame."""
        with self.engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    def execute_sql_file(self, sql_file_path: str) -> list[pd.DataFrame]:
        """Reads a .sql file containing multiple queries split by semicolon and executes each."""
        with open(sql_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        queries = [q.strip() for q in content.split(";") if q.strip() and not q.strip().startswith("--")]
        results = []
        with self.engine.connect() as conn:
            for q in queries:
                try:
                    df = pd.read_sql_query(text(q), conn)
                    results.append(df)
                except Exception as e:
                    print(f"Error executing query: {q[:50]}... Error: {e}")
        return results
