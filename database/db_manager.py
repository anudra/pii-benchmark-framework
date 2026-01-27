"""SQLite database manager."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from models.results import EvaluationResult


DB_PATH = Path(__file__).parent / "evaluations.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class DatabaseManager:
	def __init__(self, db_path: Path | None = None) -> None:
		self.db_path = db_path or DB_PATH
		self._init_db()

	def _init_db(self) -> None:
		if SCHEMA_PATH.exists():
			schema = SCHEMA_PATH.read_text(encoding="utf-8")
		else:
			schema = """
			CREATE TABLE IF NOT EXISTS evaluations (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp TEXT NOT NULL,
				model_name TEXT,
				matching_strategy TEXT,
				precision REAL,
				recall REAL,
				f1_score REAL,
				redaction_quality REAL,
				payload_json TEXT
			);
			"""
		with sqlite3.connect(self.db_path) as conn:
			conn.executescript(schema)

	def save_evaluation(self, result: EvaluationResult, model_name: str | None = None) -> int:
		payload = result.model_dump() if hasattr(result, "model_dump") else result.dict()
		payload_json = json.dumps(payload, default=str)

		with sqlite3.connect(self.db_path) as conn:
			cur = conn.cursor()
			cur.execute(
				"""
				INSERT INTO evaluations (
					timestamp, model_name, matching_strategy, precision, recall, f1_score, redaction_quality, payload_json
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(
					result.evaluation_timestamp,
					model_name,
					result.matching_strategy,
					result.overall_metrics.precision,
					result.overall_metrics.recall,
					result.overall_metrics.f1_score,
					result.redaction_quality_score,
					payload_json,
				),
			)
			conn.commit()
			return cur.lastrowid

	def list_evaluations(self) -> List[Dict[str, Any]]:
		with sqlite3.connect(self.db_path) as conn:
			conn.row_factory = sqlite3.Row
			rows = conn.execute(
				"""
				SELECT id, timestamp, model_name, matching_strategy, precision, recall, f1_score, redaction_quality
				FROM evaluations
				ORDER BY id DESC
				"""
			).fetchall()
			return [dict(r) for r in rows]

	def get_evaluation(self, eval_id: int) -> Dict[str, Any] | None:
		with sqlite3.connect(self.db_path) as conn:
			conn.row_factory = sqlite3.Row
			row = conn.execute(
				"SELECT id, timestamp, model_name, matching_strategy, payload_json FROM evaluations WHERE id = ?",
				(eval_id,),
			).fetchone()
			if not row:
				return None
			data = dict(row)
			data["payload"] = json.loads(data.get("payload_json") or "{}")
			return data
