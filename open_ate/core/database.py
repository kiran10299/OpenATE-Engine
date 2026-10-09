import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from open_ate.core.sequence import StepResult, TestStatus

class TestDatabase:
    """SQLite time-series storage for ATE Test Runs and Measurement Records."""

    def __init__(self, db_path: str = "open_ate_results.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    uut_serial TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    duration_sec REAL NOT NULL
                )
            """)
            # Measurements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    measured_value REAL,
                    low_limit REAL,
                    high_limit REAL,
                    unit TEXT,
                    duration_sec REAL,
                    FOREIGN KEY (run_id) REFERENCES test_runs(id)
                )
            """)
            conn.commit()

    def record_run(
        self,
        test_name: str,
        uut_serial: str,
        operator: str,
        verdict: str,
        start_time: datetime.datetime,
        duration_sec: float,
        step_results: List[StepResult]
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_runs (test_name, uut_serial, operator, verdict, start_time, duration_sec)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_name, uut_serial, operator, verdict, start_time.isoformat(), duration_sec))
            run_id = cursor.lastrowid

            for res in step_results:
                low = res.limit.low_limit if res.limit else None
                high = res.limit.high_limit if res.limit else None
                unit = res.limit.unit if res.limit else ""
                cursor.execute("""
                    INSERT INTO test_measurements (run_id, step_name, status, measured_value, low_limit, high_limit, unit, duration_sec)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (run_id, res.step_name, res.status.value, res.measured_value, low, high, unit, res.duration_seconds))

            conn.commit()
            return run_id
