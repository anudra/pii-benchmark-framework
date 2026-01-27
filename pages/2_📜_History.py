"""History page for previous evaluations."""
import streamlit as st

from database.db_manager import DatabaseManager

st.title("📜 Evaluation History")
db = DatabaseManager()

history = db.list_evaluations()
if not history:
	st.info("No evaluations saved yet.")
	st.stop()

st.dataframe(history, width="stretch")

selected_id = st.number_input("Enter evaluation ID to view details", min_value=1, step=1)
if st.button("View Details"):
	evaluation = db.get_evaluation(int(selected_id))
	if not evaluation:
		st.error("Evaluation not found")
	else:
		st.subheader(f"Evaluation ID {evaluation['id']}")
		st.json(evaluation.get("payload", {}))
