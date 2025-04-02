import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from src.storage.database import Database
from src.alerts.alert_manager import AlertManager

class AnomalyDetector:
    def __init__(self):
        self.db = Database()
        self.alert_manager = AlertManager()
        self.running = False
        
        # Define thresholds for different metrics
        self.thresholds = {
            "response_time": {
                "critical": 1000,  # ms
                "warning": 500     # ms
            },
            "error_rate": {
                "critical": 0.1,   # 10%
                "warning": 0.05    # 5%
            },
            "request_rate": {
                "min": 1,         # requests per minute
                "max": 1000       # requests per minute
            }
        }

    async def start(self):
        """Start the anomaly detection process"""
        self.running = True
        asyncio.create_task(self._detect_anomalies())

    async def stop(self):
        """Stop the anomaly detection process"""
        self.running = False

    async def _detect_anomalies(self):
        """Main anomaly detection loop"""
        while self.running:
            try:
                metrics = await self.db.get_recent_metrics()
                await self._analyze_metrics(metrics)
            except Exception as e:
                print(f"Error in anomaly detection: {e}")
            await asyncio.sleep(10)  # Check every 10 seconds

    async def _analyze_metrics(self, metrics: Dict):
        """Analyze metrics for anomalies"""
        for service, service_metrics in metrics.items():
            # Analyze response times
            if service_metrics["response_times"]:
                avg_response_time = np.mean(service_metrics["response_times"])
                if avg_response_time > self.thresholds["response_time"]["critical"]:
                    await self._create_alert(
                        service,
                        "Critical: High Response Time",
                        f"Average response time ({avg_response_time:.2f}ms) exceeds critical threshold",
                        "critical"
                    )
                elif avg_response_time > self.thresholds["response_time"]["warning"]:
                    await self._create_alert(
                        service,
                        "Warning: Elevated Response Time",
                        f"Average response time ({avg_response_time:.2f}ms) exceeds warning threshold",
                        "warning"
                    )

            # Analyze error rates
            if service_metrics["error_rates"]:
                error_rate = sum(service_metrics["error_rates"]) / len(service_metrics["error_rates"])
                if error_rate > self.thresholds["error_rate"]["critical"]:
                    await self._create_alert(
                        service,
                        "Critical: High Error Rate",
                        f"Error rate ({error_rate:.2%}) exceeds critical threshold",
                        "critical"
                    )
                elif error_rate > self.thresholds["error_rate"]["warning"]:
                    await self._create_alert(
                        service,
                        "Warning: Elevated Error Rate",
                        f"Error rate ({error_rate:.2%}) exceeds warning threshold",
                        "warning"
                    )

            # Analyze request rates
            if service_metrics["request_rates"]:
                request_rate = len(service_metrics["request_rates"]) / 5  # per minute
                if request_rate > self.thresholds["request_rate"]["max"]:
                    await self._create_alert(
                        service,
                        "Warning: High Request Rate",
                        f"Request rate ({request_rate:.2f}/min) exceeds maximum threshold",
                        "warning"
                    )
                elif request_rate < self.thresholds["request_rate"]["min"]:
                    await self._create_alert(
                        service,
                        "Warning: Low Request Rate",
                        f"Request rate ({request_rate:.2f}/min) below minimum threshold",
                        "warning"
                    )

    async def _create_alert(self, service: str, title: str, message: str, severity: str):
        """Create a new alert"""
        alert = {
            "service": service,
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow(),
            "metrics": await self.db.get_recent_metrics()
        }
        await self.alert_manager.create_alert(alert)
