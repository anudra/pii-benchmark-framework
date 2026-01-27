"""Main Streamlit entry point."""
from __future__ import annotations

import json
import streamlit as st

from database.db_manager import DatabaseManager
from evaluator.metrics_calculator import MetricsCalculator
from models.ground_truth import GroundTruth
from models.prediction import SystemOutput
from models.redaction import RedactedDocument
from ui.components import (
	display_metric_card,
	display_error_list,
	create_metrics_bar_chart,
)
from ui.utils import load_json_file, export_results_json
from utils.validators import validate_ground_truth, validate_predictions, validate_redacted


def normalize_ground_truth(items):
	normalized = []
	for item in items:
		payload = dict(item)
		if "document_id" in payload and "doc_id" not in payload:
			payload["doc_id"] = payload.pop("document_id")
		normalized.append(payload)
	return normalized


def normalize_text(text: str) -> str:
	return " ".join((text or "").split())


def normalize_predictions(items):
	normalized = []
	for item in items:
		payload = dict(item)
		if "document_id" in payload and "doc_id" not in payload:
			payload["doc_id"] = payload.pop("document_id")
		if "detected_entities" in payload and "predictions" not in payload:
			payload["predictions"] = payload.pop("detected_entities")
		normalized.append(payload)
	return normalized


st.set_page_config(page_title="PII Evaluation Framework", page_icon="🔍", layout="wide")

st.title("🔍 PII Detection & Redaction Evaluation Framework")
st.caption("Benchmark detection accuracy and redaction quality")

db = DatabaseManager()

st.sidebar.header("⚙️ Configuration")
model_name = st.sidebar.text_input("Model/System name", value="")
matching_strategy = st.sidebar.selectbox("Matching Strategy", ["strict", "lenient", "token"])

iou_threshold = 0.5
token_threshold = 0.5
if matching_strategy == "lenient":
	iou_threshold = st.sidebar.slider("IoU Threshold", 0.1, 1.0, 0.5, 0.05)
if matching_strategy == "token":
	token_threshold = st.sidebar.slider("Token Overlap Threshold", 0.1, 1.0, 0.5, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("Uploads: Ground Truth + Predictions (+ Redacted docs optional)")

st.subheader("📥 Original Documents (.txt)")
doc_file = st.file_uploader("Upload original text file", type=["txt"], key="doc_txt")
doc_text = None
if doc_file:
	doc_text = doc_file.getvalue().decode("utf-8")
	with st.expander("Preview original document"):
		st.text(doc_text)

red_txt_file = st.file_uploader("Upload redacted text file (optional)", type=["txt"], key="red_txt")
red_txt = None
if red_txt_file:
	red_txt = red_txt_file.getvalue().decode("utf-8")
	with st.expander("Preview redacted document"):
		st.text(red_txt)

col1, col2, col3 = st.columns(3)
with col1:
	st.subheader("📄 Ground Truth")
	gt_file = st.file_uploader("Ground truth JSON", type=["json"], key="gt")

with col2:
	st.subheader("🤖 Predictions")
	pred_file = st.file_uploader("Predictions JSON", type=["json"], key="pred")

with col3:
	st.subheader("🧼 Redacted Docs (optional)")
	red_file = st.file_uploader("Redacted JSON", type=["json"], key="red")

st.markdown("---")
if st.button("📂 Load Sample Data"):
	with open("data/sample_ground_truth.json", "r", encoding="utf-8") as f:
		st.session_state["sample_gt"] = f.read()
	with open("data/sample_predictions.json", "r", encoding="utf-8") as f:
		st.session_state["sample_pred"] = f.read()
	with open("data/original.txt", "r", encoding="utf-8") as f:
		st.session_state["sample_doc"] = f.read()
	with open("data/redacted.txt", "r", encoding="utf-8") as f:
		st.session_state["sample_red_txt"] = f.read()
	st.success("Sample data loaded. Click Evaluate.")

if st.button("🚀 Evaluate", type="primary"):
	try:
		if gt_file:
			gt_data = load_json_file(gt_file)
		elif "sample_gt" in st.session_state:
			gt_data = json.loads(st.session_state["sample_gt"])
		else:
			st.error("Please upload ground truth or load sample data.")
			st.stop()

		if pred_file:
			pred_data = load_json_file(pred_file)
		elif "sample_pred" in st.session_state:
			pred_data = json.loads(st.session_state["sample_pred"])
		else:
			st.error("Please upload predictions or load sample data.")
			st.stop()

		red_data = None
		if red_file:
			red_data = load_json_file(red_file)
		elif red_txt:
			red_data = [{"text": doc_text or "", "redacted_text": red_txt, "redacted_spans": []}]
		elif "sample_red_txt" in st.session_state:
			red_data = [{"text": st.session_state.get("sample_doc", ""), "redacted_text": st.session_state["sample_red_txt"], "redacted_spans": []}]

		validate_ground_truth(gt_data)
		validate_predictions(pred_data)
		if red_data is not None:
			validate_redacted(red_data)

		gt_data = normalize_ground_truth(gt_data)
		pred_data = normalize_predictions(pred_data)

		ground_truths = [GroundTruth(**doc) for doc in gt_data]
		predictions = [SystemOutput(**doc) for doc in pred_data]
		redacted_docs = [RedactedDocument(**doc) for doc in red_data] if red_data else None

		if not doc_text and "sample_doc" in st.session_state:
			doc_text = st.session_state["sample_doc"]

		# If user provided original/redacted txt with single-doc JSONs, align doc_id to avoid hash mismatch
		if doc_text and len(ground_truths) == 1 and len(predictions) == 1:
			predictions[0].doc_id = ground_truths[0].doc_id
			if redacted_docs and len(redacted_docs) == 1:
				redacted_docs[0].doc_id = ground_truths[0].doc_id

		if doc_text:
			doc_norm = normalize_text(doc_text)
			gt_norm = normalize_text(ground_truths[0].text) if ground_truths else ""
			pred_norm = normalize_text(predictions[0].text) if predictions else ""
			red_norm = normalize_text(redacted_docs[0].text) if redacted_docs else ""

			if ground_truths and gt_norm != doc_norm:
				st.warning("Original .txt does not match ground truth text. Proceeding with ground truth text.")
			if predictions and pred_norm != doc_norm:
				st.warning("Original .txt does not match predictions text. Proceeding with predictions text.")
			if redacted_docs and red_norm != doc_norm:
				st.warning("Original .txt does not match redacted document text. Proceeding with redacted text.")

		calculator = MetricsCalculator(
			matching_strategy=matching_strategy,
			iou_threshold=iou_threshold,
			token_threshold=token_threshold,
		)

		with st.spinner("Evaluating..."):
			results = calculator.evaluate_with_redaction(ground_truths, predictions, redacted_docs)

		eval_id = db.save_evaluation(results, model_name or None)
		st.success(f"✅ Evaluation complete. Saved as ID {eval_id}.")

		st.header("📊 Results")
		overall = results.overall_metrics
		c1, c2, c3, c4 = st.columns(4)
		with c1:
			display_metric_card("Precision", overall.precision)
		with c2:
			display_metric_card("Recall", overall.recall)
		with c3:
			display_metric_card("F1 Score", overall.f1_score)
		with c4:
			st.metric("Docs", results.total_documents)

		st.markdown("---")
		st.subheader("Per-Entity Metrics")
		per_entity_rows = []
		for entity_type, metrics in results.per_entity_metrics.items():
			per_entity_rows.append({
				"Entity Type": entity_type,
				"Precision": f"{metrics.precision:.3f}",
				"Recall": f"{metrics.recall:.3f}",
				"F1": f"{metrics.f1_score:.3f}",
				"TP": metrics.true_positives,
				"FP": metrics.false_positives,
				"FN": metrics.false_negatives,
			})
		st.dataframe(per_entity_rows, width="stretch")

		if results.per_entity_metrics:
			f1_scores = {k: v.f1_score for k, v in results.per_entity_metrics.items()}
			fig = create_metrics_bar_chart(f1_scores, "F1 Score by Entity Type")
			st.plotly_chart(fig)

		st.markdown("---")
		st.subheader("Error Analysis")
		col_a, col_b = st.columns(2)
		with col_a:
			display_error_list([str(e) for e in results.false_positives], "False Positives")
		with col_b:
			display_error_list([str(e) for e in results.false_negatives], "False Negatives")

		if results.redaction_quality_score is not None:
			st.markdown("---")
			st.subheader("Redaction Quality")
			st.metric("Redaction Quality Score", f"{results.redaction_quality_score:.3f}")
			display_error_list([str(e) for e in results.redaction_errors], "Redaction Errors")

		st.markdown("---")
		if st.button("💾 Export Results JSON"):
			st.download_button(
				"Download JSON",
				data=export_results_json(results),
				file_name=f"evaluation_{results.evaluation_timestamp}.json",
				mime="application/json",
			)

	except Exception as exc:
		st.error(f"Error: {exc}")
		st.exception(exc)
