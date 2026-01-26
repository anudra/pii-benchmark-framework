# Project Plan

## 3-Day Development Plan

Building this framework in 3 days to get an MVP ready.

---

## Day 1: Backend Stuff

**What I'm building:** The core logic that does the evaluation

**Tasks:**
- Set up project structure and install packages
- Create data models using Pydantic
- Write the span matching logic (exact and partial match)
- Build the metrics calculator (Precision, Recall, F1)

**Goal by EOD:** Have a working backend that can take JSON inputs and output metrics

---

## Day 2: Connect Everything + Start UI

**What I'm building:** Make the backend work with a simple web interface

**Tasks:**
- Create the main evaluation engine that ties everything together
- Set up Streamlit and get the basic app running
- Add file upload for ground truth and predictions
- Connect the UI to backend evaluation logic

**Goal by EOD:** Users can upload files and see basic evaluation results

---

## Day 3: Dashboard + Deployment

**What I'm building:** Make it look good and deployable

**Tasks:**
- Build the dashboard to show metrics nicely
- Add charts using Plotly
- Show error breakdowns (false positives/negatives)
- Create some sample test data
- Get Docker working

**Goal by EOD:** Full working app that runs in Docker

---

## What's Included (MVP)

Things I'm definitely building:
- ✅ Upload JSON files (ground truth + predictions)
- ✅ Two matching strategies (exact and partial overlap)
- ✅ Calculate Precision, Recall, F1-Score
- ✅ Show per-entity breakdown (EMAIL, PAN, PHONE, etc.)
- ✅ Simple dashboard with metrics and charts
- ✅ Docker deployment

What I'm skipping for now:
- ❌ Multi-page Streamlit app (keeping it simple, single page)
- ❌ Redaction validation feature
- ❌ Advanced visualizations
- ❌ Comprehensive test suite (just basic testing)

---

## Success Checklist

By the end of Day 3, I should be able to:
- [ ] Upload ground truth and prediction files
- [ ] See overall accuracy metrics
- [ ] See per-entity performance breakdown
- [ ] View lists of false positives and false negatives
- [ ] Run everything in Docker
- [ ] Have sample data to demo

---