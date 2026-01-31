# Software Requirements Specification (SRS)

## PII Benchmark Framework

**Version:** 1.0  
**Date:** January 27, 2026  
**Prepared by:** Development Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Data Requirements](#6-data-requirements)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a comprehensive description of the PII Benchmark Framework. The system is designed to evaluate and benchmark PII (Personally Identifiable Information) detection models by assessing both entity detection accuracy and redaction quality.

### 1.2 Scope

The PII Benchmark Framework is a web-based evaluation system that:

- Accepts original text, redacted text, ground truth annotations, and predicted annotations as input
- Evaluates PII detection accuracy using standard classification metrics
- Assesses redaction quality by comparing actual redactions against expected redactions
- Provides comprehensive visualizations including confusion matrices, trend charts, and text comparisons
- Generates detailed PDF reports for evaluation results
- Maintains evaluation history for comparative analysis

### 1.3 Definitions, Acronyms, and Abbreviations

- **PII**: Personally Identifiable Information
- **TP**: True Positive - Correctly identified PII
- **TN**: True Negative - Correctly identified non-PII
- **FP**: False Positive - Incorrectly identified as PII
- **FN**: False Negative - Missed PII entities
- **F1-Score**: Harmonic mean of precision and recall
- **SRS**: Software Requirements Specification
- **API**: Application Programming Interface
- **UI**: User Interface

### 1.4 References

- FastAPI Documentation
- Chart.js Documentation
- xhtml2pdf Documentation
- SQLite Documentation

---

## 2. Overall Description

### 2.1 Product Perspective

The PII Benchmark Framework operates as a standalone web application with:

- **Backend**: FastAPI-based REST API server
- **Frontend**: HTML5, CSS3, JavaScript with Chart.js for visualizations
- **Database**: SQLite for persistent storage
- **PDF Generation**: xhtml2pdf for report generation

### 2.2 Product Functions

The system provides the following major functions:

1. **Evaluation Management**
   - Upload and process evaluation data (original text, redacted text, annotations)
   - Execute PII detection and redaction quality assessments
   - Store evaluation results in database

2. **Metrics Calculation**
   - Detection Metrics: Precision, Recall, F1-Score, Accuracy
   - Redaction Metrics: Redaction Accuracy, Leak Rate, Quality Issues
   - Confusion Matrix: TP, TN, FP, FN classification

3. **Visualization & Reporting**
   - Dashboard with overview statistics and charts
   - Evaluation history with comparative metrics
   - Side-by-side evaluation comparison
   - Color-coded text difference visualization
   - PDF report generation with comprehensive metrics

4. **Data Management**
   - Persistent storage of evaluation results
   - Retrieval of historical evaluations
   - Error tracking and categorization

### 2.3 User Characteristics

**Primary Users**: Data Scientists, ML Engineers, Quality Assurance Teams

- Technical proficiency in machine learning and NLP concepts
- Understanding of PII detection and privacy compliance
- Ability to interpret classification metrics and confusion matrices

### 2.4 Constraints

- Browser compatibility: Modern browsers (Chrome, Firefox, Edge, Safari)
- Server platform: Windows, Linux, macOS
- Python version: 3.8+
- Database: SQLite (single-file database)

### 2.5 Assumptions and Dependencies

- Users have access to ground truth annotations
- Input text files use UTF-8 encoding
- Predicted and ground truth annotations follow the same format
- Server has sufficient storage for evaluation history

---

## 3. System Features

### 3.1 Dashboard

**Priority**: High

#### 3.1.1 Description

The dashboard serves as the landing page, providing an at-a-glance overview of system performance and recent activity.

#### 3.1.2 Functional Requirements

- **FR-1.1**: System shall display total number of evaluations
- **FR-1.2**: System shall calculate and display average detection accuracy across all evaluations
- **FR-1.3**: System shall calculate and display average redaction accuracy across all evaluations
- **FR-1.4**: System shall display total error count
- **FR-1.5**: System shall render a line chart showing detection vs redaction accuracy trends over the last 10 evaluations
- **FR-1.6**: System shall render a bar chart comparing average performance across different models
- **FR-1.7**: System shall render a doughnut chart showing error distribution by type
- **FR-1.8**: System shall display a table of the 5 most recent evaluations
- **FR-1.9**: System shall provide quick action buttons to navigate to Upload, History, and Compare pages
- **FR-1.10**: Dashboard shall be accessible via root URL ("/")

### 3.2 Evaluation Upload and Execution

**Priority**: High

#### 3.2.1 Description

Users can upload evaluation data files and execute PII detection and redaction quality assessments.

#### 3.2.2 Functional Requirements

- **FR-2.1**: System shall accept file uploads for original text, redacted text, ground truth annotations, and predicted annotations
- **FR-2.2**: System shall validate that original and redacted text have equal length
- **FR-2.3**: System shall validate JSON format for annotation files
- **FR-2.4**: System shall allow users to specify model name and evaluation mode (strict/lenient)
- **FR-2.5**: System shall calculate detection metrics: precision, recall, F1-score, accuracy
- **FR-2.6**: System shall generate confusion matrix (TP, TN, FP, FN)
- **FR-2.7**: System shall analyze redaction quality and categorize entities as: correct, leak, over-redacted, under-redacted, semi-redacted
- **FR-2.8**: System shall generate color-coded HTML diff comparing original and redacted text
- **FR-2.9**: System shall store evaluation results in database
- **FR-2.10**: System shall display loading indicator during evaluation processing
- **FR-2.11**: System shall display error messages if evaluation fails

### 3.3 Evaluation Results

**Priority**: High

#### 3.3.1 Description

Users can view detailed results of individual evaluations including metrics, visualizations, and text comparisons.

#### 3.3.2 Functional Requirements

- **FR-3.1**: System shall display evaluation metadata (ID, model name, mode, timestamp)
- **FR-3.2**: System shall display detection metrics in separate section
- **FR-3.3**: System shall display redaction metrics in separate section
- **FR-3.4**: System shall render confusion matrix as 2x2 grid with color coding:
  - Green background for TP and TN (correct classifications)
  - Red background for FP and FN (errors)
- **FR-3.5**: System shall display TP, TN, FP, FN labels within confusion matrix cells
- **FR-3.6**: System shall provide legend explaining confusion matrix terms
- **FR-3.7**: System shall display color-coded text diff with:
  - Green highlighting for correct redactions
  - Red highlighting for data leaks
  - Yellow highlighting for over-redactions
  - Orange highlighting for under-redactions and semi-redactions
- **FR-3.8**: System shall display diff legend explaining color codes
- **FR-3.9**: System shall show side-by-side comparison of original and redacted text
- **FR-3.10**: System shall list all detected errors with entity type, position, and description
- **FR-3.11**: System shall provide "Export PDF" button
- **FR-3.12**: System shall provide "Back to History" navigation button

### 3.4 Evaluation History

**Priority**: High

#### 3.4.1 Description

Users can view a chronological list of all evaluations with comparative metrics.

#### 3.4.2 Functional Requirements

- **FR-4.1**: System shall display table of all evaluations sorted by date (newest first)
- **FR-4.2**: System shall display following columns for each evaluation:
  - Evaluation ID
  - Model Name
  - Evaluation Mode
  - Detection Accuracy (color-coded green)
  - Redaction Accuracy (color-coded orange)
  - Error Count
  - Timestamp
- **FR-4.3**: System shall separate Detection Accuracy and Redaction Accuracy into distinct columns
- **FR-4.4**: System shall calculate Detection Accuracy from detection metrics
- **FR-4.5**: System shall calculate Redaction Accuracy from redaction quality score
- **FR-4.6**: System shall provide "View" action button for each evaluation
- **FR-4.7**: System shall provide navigation to dashboard and compare pages

### 3.5 Evaluation Comparison

**Priority**: Medium

#### 3.5.1 Description

Users can select two evaluations and view side-by-side comparison of their metrics and results.

#### 3.5.2 Functional Requirements

- **FR-5.1**: System shall provide dropdown selectors for two evaluations
- **FR-5.2**: System shall display metrics for both evaluations in side-by-side columns
- **FR-5.3**: System shall render comparison charts showing detection and redaction metrics
- **FR-5.4**: System shall highlight differences between the two evaluations
- **FR-5.5**: System shall display confusion matrices for both evaluations
- **FR-5.6**: System shall show text diffs for both evaluations

### 3.6 PDF Report Generation

**Priority**: High

#### 3.6.1 Description

Users can export evaluation results as professionally formatted PDF documents.

#### 3.6.2 Functional Requirements

- **FR-6.1**: System shall generate PDF reports using xhtml2pdf library
- **FR-6.2**: PDF shall include evaluation metadata (ID, model, mode, timestamp)
- **FR-6.3**: PDF shall include section 1: Entity Detection Evaluation with:
  - Detection metrics (precision, recall, F1-score, accuracy)
  - Confusion matrix table
  - Metric descriptions
- **FR-6.4**: PDF shall include section 2: Redaction Quality Evaluation with:
  - Redaction metrics (accuracy, leak rate, quality issues, total entities)
  - Redaction status summary table
- **FR-6.5**: PDF shall include section 3: Text Comparison with color-coded diff visualization
- **FR-6.6**: PDF shall include section 4: Errors Summary with detailed error table
- **FR-6.7**: PDF shall use simple, clean formatting with:
  - Black text on white background
  - Basic bordered tables
  - Clear section headings
  - Numbered sections
- **FR-6.8**: PDF confusion matrix shall use properly aligned table with:
  - Empty top-left header cell
  - "Predicted Positive" and "Predicted Negative" column headers
  - "Actual Positive" and "Actual Negative" row labels
  - TP, FN, FP, TN values in appropriate cells
- **FR-6.9**: System shall return PDF with correct MIME type (application/pdf)
- **FR-6.10**: System shall provide fallback to HTML if PDF generation fails
- **FR-6.11**: PDF filename shall follow format: evaluation_{id}.pdf

---

## 4. External Interface Requirements

### 4.1 User Interface Requirements

#### 4.1.1 General UI Requirements

- **UI-1**: All pages shall have consistent navigation bar with links to Dashboard, Upload, History, and Compare
- **UI-2**: System shall use professional, clean design without emoji decorations
- **UI-3**: All text shall be readable with sufficient contrast
- **UI-4**: Forms shall provide clear labels and placeholders
- **UI-5**: System shall display loading indicators for asynchronous operations
- **UI-6**: Error messages shall be displayed clearly to users

#### 4.1.2 Dashboard UI

- **UI-7**: Dashboard shall display statistics in card layout
- **UI-8**: Charts shall be rendered using Chart.js library
- **UI-9**: Quick action buttons shall be clearly visible
- **UI-10**: Recent evaluations table shall show 5 latest entries

#### 4.1.3 Results UI

- **UI-11**: Confusion matrix shall be displayed as 2x2 grid with clear visual separation
- **UI-12**: Color coding shall be consistent across all visualizations
- **UI-13**: Text diff shall show original and redacted text side-by-side

### 4.2 API Requirements

#### 4.2.1 Endpoints

- **API-1**: `POST /api/evaluate` - Submit new evaluation
- **API-2**: `GET /api/results/{id}` - Retrieve evaluation results
- **API-3**: `GET /api/history` - Retrieve all evaluations
- **API-4**: `GET /api/compare/{id1}/{id2}` - Compare two evaluations
- **API-5**: `GET /api/export/{id}/json` - Export evaluation as JSON
- **API-6**: `GET /api/export/{id}/pdf` - Export evaluation as PDF
- **API-7**: `GET /api/dashboard/stats` - Retrieve dashboard statistics

#### 4.2.2 Response Format

- All API responses shall use JSON format (except PDF export)
- Error responses shall include error message and HTTP status code
- Success responses shall include relevant data and status

### 4.3 Database Requirements

- **DB-1**: Database file shall be stored at project root: `evaluations.db`
- **DB-2**: Database shall use SQLite engine
- **DB-3**: Schema shall include tables for: Evaluation, Result, Error
- **DB-4**: All JSON data shall be serialized before storage
- **DB-5**: Timestamps shall be stored in ISO format

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

- **NFR-1**: Evaluation processing shall complete within 10 seconds for files under 1MB
- **NFR-2**: Dashboard shall load statistics within 2 seconds
- **NFR-3**: PDF generation shall complete within 5 seconds
- **NFR-4**: API response time shall be under 1 second for data retrieval operations

### 5.2 Security Requirements

- **NFR-5**: All file uploads shall be validated for size and type
- **NFR-6**: System shall sanitize user inputs to prevent injection attacks
- **NFR-7**: Database queries shall use parameterized statements

### 5.3 Reliability Requirements

- **NFR-8**: System shall handle invalid input gracefully with appropriate error messages
- **NFR-9**: Database operations shall use transactions to ensure data consistency
- **NFR-10**: System shall provide fallback to HTML if PDF generation fails

### 5.4 Maintainability Requirements

- **NFR-11**: Code shall follow PEP 8 style guidelines for Python
- **NFR-12**: Frontend code shall use modular JavaScript structure
- **NFR-13**: API routes shall be organized logically
- **NFR-14**: Database models shall use SQLAlchemy ORM

### 5.5 Portability Requirements

- **NFR-15**: System shall run on Windows, Linux, and macOS
- **NFR-16**: Frontend shall be compatible with Chrome, Firefox, Edge, and Safari
- **NFR-17**: PDF generation shall work without external dependencies (using pure Python library)

### 5.6 Usability Requirements

- **NFR-18**: Navigation shall be intuitive with clear labels
- **NFR-19**: Color coding shall be consistent and meaningful
- **NFR-20**: Dashboard shall provide quick access to common tasks
- **NFR-21**: Error messages shall be user-friendly and actionable

---

## 6. Data Requirements

### 6.1 Input Data

#### 6.1.1 Text Files

- Original text and redacted text must have equal character length
- UTF-8 encoding required
- Maximum file size: 10MB

#### 6.1.2 Annotation Files

- JSON format with array of annotation objects
- Each annotation must include: entity_type, start, end
- Optional fields: text, label
- Start and end positions must be valid indices

### 6.2 Stored Data

#### 6.2.1 Evaluation Data

- Evaluation ID (auto-generated)
- Model name (string)
- Evaluation mode (strict/lenient)
- Timestamp (ISO format)

#### 6.2.2 Metrics Data

- Detection metrics: precision, recall, F1-score, accuracy (float 0-1)
- Confusion matrix: TP, TN, FP, FN (integers)
- Redaction summary: total entities, correct, leaks, over, under, semi (integers)
- Redaction quality score (float 0-1)

#### 6.2.3 Analysis Data

- Per-entity metrics (JSON)
- Redaction categories: correct, leak, over, under, semi (JSON arrays)
- Diff HTML (text)

#### 6.2.4 Error Data

- Error type (string)
- Entity type (string)
- Position start/end (integers)
- Text snippet (string)
- Description (string)

### 6.3 Output Data

#### 6.3.1 JSON Export

- Complete evaluation data including all metrics and analysis
- Separate sections for detection and redaction evaluation
- Error details

#### 6.3.2 PDF Export

- Formatted report with all sections
- Tables and metrics
- Color-coded diff visualization
- Legend and descriptions

---

## Appendix A: Metric Definitions

### Detection Metrics

- **Precision**: TP / (TP + FP) - Percentage of predicted PII that is actually PII
- **Recall**: TP / (TP + FN) - Percentage of actual PII that was detected
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall) - Harmonic mean
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN) - Overall correctness

### Redaction Categories

- **Correct**: PII properly redacted with exact replacement
- **Leak**: PII not redacted at all (critical security issue)
- **Over-redacted**: More characters redacted than necessary
- **Under-redacted**: PII partially visible (security risk)
- **Semi-redacted**: Mostly redacted but some characters visible

---

## Appendix B: Color Coding Standards

### UI Color Codes

- **Green (#4CAF50)**: Positive/correct (TP, TN, correct redactions, detection accuracy)
- **Red (#F44336)**: Critical errors (FP, FN, leaks)
- **Orange (#FF9800)**: Warnings (under-redactions, redaction accuracy)
- **Yellow (#FFC107)**: Minor issues (over-redactions)
- **Blue (#2196F3)**: Informational (total entities, neutral data)

### Text Diff Color Codes

- **Green (#4CAF50)**: Correct redactions
- **Red (#F44336)**: Data leaks
- **Yellow (#FFC107)**: Over-redactions
- **Orange (#FF9800)**: Under-redactions
- **Light Orange (#FFB74D)**: Semi-redactions

---
