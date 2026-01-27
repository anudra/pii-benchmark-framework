"""Compare two evaluations."""
import streamlit as st

from database.db_manager import DatabaseManager

st.title("📈 Compare Evaluations")
db = DatabaseManager()
history = db.list_evaluations()

if len(history) < 2:
	st.info("Need at least 2 evaluations to compare.")
	st.stop()

ids = [item["id"] for item in history]
left_id = st.selectbox("Select first evaluation", ids, key="left")
right_id = st.selectbox("Select second evaluation", ids, key="right")

left_eval = db.get_evaluation(int(left_id))
right_eval = db.get_evaluation(int(right_id))

col1, col2 = st.columns(2)
with col1:
	st.subheader(f"Evaluation {left_id}")
	st.json(left_eval.get("payload", {}))
with col2:
	st.subheader(f"Evaluation {right_id}")
	st.json(right_eval.get("payload", {}))
