from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from typing import Dict, List
from datetime import datetime
from src.storage.database import Database
from src.analyzers.anomaly_detector import AnomalyDetector
from src.predictors.predictor import Predictor

router = APIRouter()
db = Database()
anomaly_detector = AnomalyDetector()
predictor = Predictor()

@router.get("/")
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(datetime.timezone.utc)}

@router.get("/metrics/{service}")
async def get_service_metrics(service: str):
    """Get metrics for a specific service"""
    metrics = await db.get_recent_metrics()
    if service not in metrics:
        raise HTTPException(status_code=404, detail="Service not found")
    return metrics[service]

@router.get("/alerts")
async def get_alerts(status: str = None):
    """Get all active alerts"""
    alerts = await db.get_active_alerts()
    if status:
        alerts = [a for a in alerts if a.get("status") == status]
    return alerts

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    await db.update_alert_status(alert_id, "acknowledged")
    return {"status": "success"}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    await db.update_alert_status(alert_id, "resolved")
    return {"status": "success"}

@router.get("/predictions/{service}")
async def get_predictions(service: str):
    """Get predictions for a specific service"""
    current_metrics = await db.get_recent_metrics()
    if service not in current_metrics:
        raise HTTPException(status_code=404, detail="Service not found")
    
    predictions = predictor._make_predictions({service: current_metrics[service]})
    return predictions[0] if predictions else {"message": "No predictions available"}
