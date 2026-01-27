"""UI components."""
from typing import Dict, List

import streamlit as st
import plotly.express as px


def display_metric_card(label: str, value: float, delta: float | None = None) -> None:
	st.metric(label=label, value=f"{value:.3f}", delta=f"{delta:.3f}" if delta is not None else None)


def display_metrics_table(metrics: List[Dict]) -> None:
	st.dataframe(metrics, width="stretch")


def create_metrics_bar_chart(metrics_data: Dict[str, float], title: str):
	fig = px.bar(
		x=list(metrics_data.keys()),
		y=list(metrics_data.values()),
		labels={"x": "Entity Type", "y": "Score"},
		title=title,
	)
	return fig


def display_error_list(errors: List[str], error_type: str) -> None:
	with st.expander(f"{error_type} ({len(errors)} found)"):
		if errors:
			for i, error in enumerate(errors, 1):
				st.write(f"**{i}.** {error}")
		else:
			st.success(f"No {error_type.lower()} found!")
