# API endpoint definitions
# Defines all REST API routes for the application

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from ..database.db import get_db
from ..database import models as db_models
from ..api import models as api_models
from ..core import validator, matcher, metrics, redaction_checker, error_analyzer, diff_generator, report_generator

router = APIRouter()


@router.post("/api/evaluate", response_model=api_models.EvaluationResponse)
async def evaluate(request: api_models.EvaluationRequest, db: Session = Depends(get_db)):
    """Run PII evaluation"""
    
    # Validate inputs
    is_valid, msg = validator.validate_all_inputs(
        request.original_text,
        request.redacted_text,
        request.ground_truth,
        request.predictions,
        request.mode
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # Extract entities
    gt_entities = request.ground_truth.get("entities", [])
    pred_entities = request.predictions.get("predictions", [])
    
    # Match entities
    match_results = matcher.match_entities(gt_entities, pred_entities, request.mode)
    
    # Calculate metrics
    metrics_result = metrics.calculate_metrics(match_results, len(request.original_text))
    
    # Analyze redaction
    redaction_analysis = redaction_checker.analyze_redaction(
        request.original_text,
        request.redacted_text,
        gt_entities,
        match_results
    )
    
    # Generate diff HTML
    diff_html = diff_generator.generate_diff_html(
        request.original_text,
        request.redacted_text,
        gt_entities,
        redaction_analysis
    )
    
    # Analyze errors
    errors = error_analyzer.analyze_errors(match_results, redaction_analysis)
    
    # Save to database
    evaluation = db_models.Evaluation(
        model_name=request.model_name,
        mode=request.mode,
        timestamp=datetime.utcnow()
    )
    db.add(evaluation)
    db.flush()
    
    # Save input files
    input_file = db_models.InputFile(
        evaluation_id=evaluation.id,
        original_text=request.original_text,
        redacted_text=request.redacted_text,
        ground_truth=json.dumps(request.ground_truth),
        predictions=json.dumps(request.predictions)
    )
    db.add(input_file)
    
    # Save results
    result = db_models.Result(
        evaluation_id=evaluation.id,
        true_positives=metrics_result["true_positives"],
        true_negatives=metrics_result["true_negatives"],
        false_positives=metrics_result["false_positives"],
        false_negatives=metrics_result["false_negatives"],
        precision=metrics_result["precision"],
        recall=metrics_result["recall"],
        f1_score=metrics_result["f1_score"],
        accuracy=metrics_result["accuracy"],
        confusion_matrix=json.dumps(metrics_result["confusion_matrix"]),
        per_entity_metrics=json.dumps(metrics_result["per_entity_metrics"]),
        redaction_analysis=json.dumps(redaction_analysis),
        diff_html=diff_html
    )
    db.add(result)
    
    # Save errors
    for error in errors:
        error_record = db_models.Error(
            evaluation_id=evaluation.id,
            error_type=error["error_type"],
            entity_type=error["entity_type"],
            position_start=error["position_start"],
            position_end=error["position_end"],
            text=error["text"],
            description=error["description"]
        )
        db.add(error_record)
    
    db.commit()
    db.refresh(evaluation)
    
    # Return response
    return api_models.EvaluationResponse(
        id=evaluation.id,
        timestamp=evaluation.timestamp,
        model_name=evaluation.model_name,
        mode=evaluation.mode,
        metrics=api_models.MetricsResponse(**metrics_result),
        confusion_matrix=metrics_result["confusion_matrix"],
        per_entity_metrics=metrics_result["per_entity_metrics"],
        redaction_analysis=redaction_analysis,
        diff_html=diff_html,
        errors=errors
    )


@router.get("/api/history", response_model=List[api_models.HistoryItem])
async def get_history(db: Session = Depends(get_db)):
    """Get all evaluations"""
    
    evaluations = db.query(db_models.Evaluation).order_by(db_models.Evaluation.timestamp.desc()).all()
    
    history = []
    for eval in evaluations:
        result = db.query(db_models.Result).filter(db_models.Result.evaluation_id == eval.id).first()
        history.append(api_models.HistoryItem(
            id=eval.id,
            timestamp=eval.timestamp,
            model_name=eval.model_name,
            mode=eval.mode,
            accuracy=result.accuracy if result else 0.0
        ))
    
    return history


@router.get("/api/evaluation/{eval_id}", response_model=api_models.EvaluationResponse)
async def get_evaluation(eval_id: int, db: Session = Depends(get_db)):
    """Get specific evaluation results"""
    
    evaluation = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    result = db.query(db_models.Result).filter(db_models.Result.evaluation_id == eval_id).first()
    errors = db.query(db_models.Error).filter(db_models.Error.evaluation_id == eval_id).all()
    
    error_list = [{
        "error_type": e.error_type,
        "entity_type": e.entity_type,
        "position_start": e.position_start,
        "position_end": e.position_end,
        "text": e.text,
        "description": e.description
    } for e in errors]
    
    return api_models.EvaluationResponse(
        id=evaluation.id,
        timestamp=evaluation.timestamp,
        model_name=evaluation.model_name,
        mode=evaluation.mode,
        metrics=api_models.MetricsResponse(
            true_positives=result.true_positives,
            true_negatives=result.true_negatives,
            false_positives=result.false_positives,
            false_negatives=result.false_negatives,
            precision=result.precision,
            recall=result.recall,
            f1_score=result.f1_score,
            accuracy=result.accuracy
        ),
        confusion_matrix=json.loads(result.confusion_matrix),
        per_entity_metrics=json.loads(result.per_entity_metrics),
        redaction_analysis=json.loads(result.redaction_analysis),
        diff_html=result.diff_html,
        errors=error_list
    )


@router.delete("/api/evaluation/{eval_id}")
async def delete_evaluation(eval_id: int, db: Session = Depends(get_db)):
    """Delete evaluation"""
    
    evaluation = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    db.delete(evaluation)
    db.commit()
    
    return {"message": "Evaluation deleted successfully"}


@router.get("/api/compare/{id1}/{id2}", response_model=api_models.ComparisonResponse)
async def compare_evaluations(id1: int, id2: int, db: Session = Depends(get_db)):
    """Compare two evaluations"""
    
    eval1 = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == id1).first()
    eval2 = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == id2).first()
    
    if not eval1 or not eval2:
        raise HTTPException(status_code=404, detail="One or both evaluations not found")
    
    result1 = db.query(db_models.Result).filter(db_models.Result.evaluation_id == id1).first()
    result2 = db.query(db_models.Result).filter(db_models.Result.evaluation_id == id2).first()
    errors1 = db.query(db_models.Error).filter(db_models.Error.evaluation_id == id1).all()
    errors2 = db.query(db_models.Error).filter(db_models.Error.evaluation_id == id2).all()
    
    # Build evaluation responses
    eval1_response = api_models.EvaluationResponse(
        id=eval1.id,
        timestamp=eval1.timestamp,
        model_name=eval1.model_name,
        mode=eval1.mode,
        metrics=api_models.MetricsResponse(
            true_positives=result1.true_positives,
            true_negatives=result1.true_negatives,
            false_positives=result1.false_positives,
            false_negatives=result1.false_negatives,
            precision=result1.precision,
            recall=result1.recall,
            f1_score=result1.f1_score,
            accuracy=result1.accuracy
        ),
        confusion_matrix=json.loads(result1.confusion_matrix),
        per_entity_metrics=json.loads(result1.per_entity_metrics),
        redaction_analysis=json.loads(result1.redaction_analysis),
        diff_html=result1.diff_html,
        errors=[{
            "error_type": e.error_type,
            "entity_type": e.entity_type,
            "position_start": e.position_start,
            "position_end": e.position_end,
            "text": e.text,
            "description": e.description
        } for e in errors1]
    )
    
    eval2_response = api_models.EvaluationResponse(
        id=eval2.id,
        timestamp=eval2.timestamp,
        model_name=eval2.model_name,
        mode=eval2.mode,
        metrics=api_models.MetricsResponse(
            true_positives=result2.true_positives,
            true_negatives=result2.true_negatives,
            false_positives=result2.false_positives,
            false_negatives=result2.false_negatives,
            precision=result2.precision,
            recall=result2.recall,
            f1_score=result2.f1_score,
            accuracy=result2.accuracy
        ),
        confusion_matrix=json.loads(result2.confusion_matrix),
        per_entity_metrics=json.loads(result2.per_entity_metrics),
        redaction_analysis=json.loads(result2.redaction_analysis),
        diff_html=result2.diff_html,
        errors=[{
            "error_type": e.error_type,
            "entity_type": e.entity_type,
            "position_start": e.position_start,
            "position_end": e.position_end,
            "text": e.text,
            "description": e.description
        } for e in errors2]
    )
    
    # Calculate differences
    differences = {
        "precision_diff": round(result2.precision - result1.precision, 4),
        "recall_diff": round(result2.recall - result1.recall, 4),
        "f1_diff": round(result2.f1_score - result1.f1_score, 4),
        "accuracy_diff": round(result2.accuracy - result1.accuracy, 4)
    }
    
    return api_models.ComparisonResponse(
        evaluation1=eval1_response,
        evaluation2=eval2_response,
        differences=differences
    )


@router.get("/api/export/{eval_id}/json")
async def export_json(eval_id: int, db: Session = Depends(get_db)):
    """Export evaluation as JSON"""
    
    evaluation = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    result = db.query(db_models.Result).filter(db_models.Result.evaluation_id == eval_id).first()
    errors = db.query(db_models.Error).filter(db_models.Error.evaluation_id == eval_id).all()
    
    evaluation_data = {
        "id": evaluation.id,
        "timestamp": evaluation.timestamp,
        "model_name": evaluation.model_name,
        "mode": evaluation.mode,
        "metrics": {
            "precision": result.precision,
            "recall": result.recall,
            "f1_score": result.f1_score,
            "accuracy": result.accuracy
        },
        "confusion_matrix": json.loads(result.confusion_matrix),
        "per_entity_metrics": json.loads(result.per_entity_metrics),
        "redaction_analysis": json.loads(result.redaction_analysis),
        "errors": [{
            "error_type": e.error_type,
            "entity_type": e.entity_type,
            "position_start": e.position_start,
            "position_end": e.position_end,
            "text": e.text,
            "description": e.description
        } for e in errors]
    }
    
    json_content = report_generator.generate_json_report(evaluation_data)
    
    return Response(content=json_content, media_type="application/json",
                   headers={"Content-Disposition": f"attachment; filename=evaluation_{eval_id}.json"})


@router.get("/api/export/{eval_id}/pdf")
async def export_pdf(eval_id: int, db: Session = Depends(get_db)):
    """Export evaluation as PDF"""
    
    evaluation = db.query(db_models.Evaluation).filter(db_models.Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    result = db.query(db_models.Result).filter(db_models.Result.evaluation_id == eval_id).first()
    errors = db.query(db_models.Error).filter(db_models.Error.evaluation_id == eval_id).all()
    
    evaluation_data = {
        "id": evaluation.id,
        "timestamp": evaluation.timestamp,
        "model_name": evaluation.model_name,
        "mode": evaluation.mode,
        "metrics": {
            "precision": result.precision,
            "recall": result.recall,
            "f1_score": result.f1_score,
            "accuracy": result.accuracy
        },
        "confusion_matrix": json.loads(result.confusion_matrix),
        "per_entity_metrics": json.loads(result.per_entity_metrics),
        "redaction_analysis": json.loads(result.redaction_analysis),
        "errors": [{
            "error_type": e.error_type,
            "entity_type": e.entity_type,
            "position_start": e.position_start,
            "position_end": e.position_end,
            "text": e.text,
            "description": e.description
        } for e in errors]
    }
    
    pdf_content = report_generator.generate_pdf_report(evaluation_data)
    
    return Response(content=pdf_content, media_type="text/html",
                   headers={"Content-Disposition": f"attachment; filename=evaluation_{eval_id}.html"})
