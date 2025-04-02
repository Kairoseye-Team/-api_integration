from typing import Dict, List
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.logs = []
        self.metrics = {}
        self.alerts = []
        
    async def store_logs(self, logs: List[Dict]):
        """Store processed logs in memory"""
        if logs:
            self.logs.extend(logs)
            # Keep only last 24 hours of logs
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.logs = [log for log in self.logs if log["timestamp"] >= cutoff]

    async def store_alert(self, alert: Dict):
        """Store an alert in memory"""
        alert["_id"] = str(len(self.alerts) + 1)  # Simple ID generation
        alert["status"] = "new"
        self.alerts.append(alert)

    async def get_logs_between(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get logs between start_time and end_time"""
        return [log for log in self.logs if start_time <= log["timestamp"] <= end_time]

    async def get_historical_metrics(self) -> Dict:
        """Get historical metrics for analysis"""
        metrics = {}
        for log in self.logs:
            service = log["service"]
            if service not in metrics:
                metrics[service] = {
                    "timestamps": [],
                    "response_times": [],
                    "error_rates": [],
                    "request_rates": [],
                    "incidents": []
                }
            
            metrics[service]["timestamps"].append(log["timestamp"])
            metrics[service]["response_times"].append(log["response_time"])
            metrics[service]["error_rates"].append(1 if log["error"] else 0)
            metrics[service]["request_rates"].append(1)  # Simplified for demo
            metrics[service]["incidents"].append(
                1 if log["error"] or log["response_time"] > 1000 else 0
            )
            
        return metrics

    async def get_recent_metrics(self) -> Dict:
        """Get metrics from the last 5 minutes"""
        start_time = datetime.utcnow() - timedelta(minutes=5)
        recent_logs = [log for log in self.logs if log["timestamp"] >= start_time]
        
        metrics = {}
        for log in recent_logs:
            service = log["service"]
            if service not in metrics:
                metrics[service] = {
                    "response_times": [],
                    "error_rates": [],
                    "request_rates": [],
                    "error_count": 0,
                    "total_requests": 0
                }
            
            metrics[service]["response_times"].append(log["response_time"])
            metrics[service]["error_rates"].append(1 if log["error"] else 0)
            metrics[service]["request_rates"].append(1)  # Simplified for demo
            if log["error"]:
                metrics[service]["error_count"] += 1
            metrics[service]["total_requests"] += 1
            
        return metrics

    async def get_active_alerts(self) -> List[Dict]:
        """Get list of active (non-resolved) alerts"""
        return [alert for alert in self.alerts if alert.get("status") != "resolved"]

    async def update_alert_status(self, alert_id: str, status: str):
        """Update the status of an alert"""
        for alert in self.alerts:
            if alert["_id"] == alert_id:
                alert["status"] = status
                alert["updated_at"] = datetime.utcnow()
                break
