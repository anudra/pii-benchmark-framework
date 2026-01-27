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
