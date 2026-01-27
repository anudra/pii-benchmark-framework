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
        timestamp=datetime.now()
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
        redaction_data = None
        if result and result.redaction_analysis:
            try:
                redaction_data = json.loads(result.redaction_analysis)
                print(f"Eval {eval.id} redaction data:", redaction_data)
            except Exception as e:
                print(f"Error parsing redaction data for eval {eval.id}: {e}")
        else:
            print(f"No redaction data for eval {eval.id}")
        
        history.append(api_models.HistoryItem(
            id=eval.id,
            timestamp=eval.timestamp,
            model_name=eval.model_name,
            mode=eval.mode,
            accuracy=result.accuracy if result else 0.0,
            redaction_analysis=redaction_data
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
        "diff_html": result.diff_html,
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
    
    # Check if it's actual PDF or HTML fallback
    if pdf_content[:4] == b'%PDF':
        media_type = "application/pdf"
        filename = f"evaluation_{eval_id}.pdf"
    else:
        media_type = "text/html"
        filename = f"evaluation_{eval_id}.html"
    
    return Response(content=pdf_content, media_type=media_type,
                   headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    evaluations = db.query(db_models.Evaluation).order_by(db_models.Evaluation.timestamp.desc()).all()
    
    if not evaluations:
        return {
            "total_evaluations": 0,
            "avg_detection_accuracy": 0.0,
            "avg_redaction_accuracy": 0.0,
            "total_errors": 0,
            "best_model": None,
            "latest_eval": None,
            "trend_data": [],
            "model_performance": {},
            "error_distribution": {
                "false_positives": 0,
                "false_negatives": 0,
                "leaks": 0,
                "over_redactions": 0,
                "under_redactions": 0
            },
            "recent_evaluations": []
        }
    
    # Calculate statistics
    total_evaluations = len(evaluations)
    total_detection = 0
    total_redaction = 0
    total_errors = 0
    model_stats = {}
    error_dist = {
        "false_positives": 0,
        "false_negatives": 0,
        "leaks": 0,
        "over_redactions": 0,
        "under_redactions": 0
    }
    
    trend_data = []
    recent_evaluations = []
    
    for eval in evaluations:
        result = db.query(db_models.Result).filter(db_models.Result.evaluation_id == eval.id).first()
        if not result:
            continue
        
        # Detection accuracy
        detection_acc = result.accuracy
        total_detection += detection_acc
        
        # Redaction accuracy
        redaction_data = json.loads(result.redaction_analysis) if result.redaction_analysis else {}
        redaction_acc = redaction_data.get('summary', {}).get('redaction_quality_score', 0)
        total_redaction += redaction_acc
        
        # Error counts
        error_count = db.query(db_models.Error).filter(db_models.Error.evaluation_id == eval.id).count()
        total_errors += error_count
        
        # Error distribution
        error_dist["false_positives"] += result.false_positives
        error_dist["false_negatives"] += result.false_negatives
        if redaction_data.get('summary'):
            error_dist["leaks"] += redaction_data['summary'].get('leaks', 0)
            error_dist["over_redactions"] += redaction_data['summary'].get('over_redactions', 0)
            error_dist["under_redactions"] += redaction_data['summary'].get('under_redactions', 0)
        
        # Model performance
        model_name = eval.model_name
        if model_name not in model_stats:
            model_stats[model_name] = {"total_detection": 0, "total_redaction": 0, "count": 0}
        model_stats[model_name]["total_detection"] += detection_acc
        model_stats[model_name]["total_redaction"] += redaction_acc
        model_stats[model_name]["count"] += 1
        
        # Trend data (last 10 evaluations)
        if len(trend_data) < 10:
            trend_data.append({
                "timestamp": eval.timestamp.isoformat(),
                "detection_accuracy": detection_acc,
                "redaction_accuracy": redaction_acc
            })
        
        # Recent evaluations (last 5)
        if len(recent_evaluations) < 5:
            recent_evaluations.append({
                "id": eval.id,
                "model_name": eval.model_name,
                "timestamp": eval.timestamp.isoformat(),
                "detection_accuracy": detection_acc,
                "redaction_accuracy": redaction_acc
            })
    
    # Calculate averages
    avg_detection = total_detection / total_evaluations if total_evaluations > 0 else 0
    avg_redaction = total_redaction / total_evaluations if total_evaluations > 0 else 0
    
    # Model performance averages
    model_performance = {}
    for model, stats in model_stats.items():
        model_performance[model] = {
            "avg_detection": stats["total_detection"] / stats["count"],
            "avg_redaction": stats["total_redaction"] / stats["count"]
        }
    
    # Best performing model (by combined average)
    best_model = None
    best_score = 0
    for model, perf in model_performance.items():
        combined = (perf["avg_detection"] + perf["avg_redaction"]) / 2
        if combined > best_score:
            best_score = combined
            best_model = model
    
    # Latest evaluation
    latest_eval = {
        "id": evaluations[0].id,
        "model_name": evaluations[0].model_name
    } if evaluations else None
    
    # Reverse trend data to show chronological order
    trend_data.reverse()
    
    return {
        "total_evaluations": total_evaluations,
        "avg_detection_accuracy": avg_detection,
        "avg_redaction_accuracy": avg_redaction,
        "total_errors": total_errors,
        "best_model": best_model,
        "latest_eval": latest_eval,
        "trend_data": trend_data,
        "model_performance": model_performance,
        "error_distribution": error_dist,
        "recent_evaluations": recent_evaluations
    }
