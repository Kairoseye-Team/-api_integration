import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import boto3
from src.config.external_services import AWS_SNS_CONFIG
from src.integrations.openai_analyzer import OpenAIAnalyzer
from src.config.external_services import OPENAI_CONFIG

class AlertManager:
    def __init__(self):
        self.alerts = []
        self.ai_analyzer = None
        if OPENAI_CONFIG["enabled"]:
            self.ai_analyzer = OpenAIAnalyzer(OPENAI_CONFIG["api_key"])
        
        # Initialize SNS client if configured
        self.sns_client = None
        if AWS_SNS_CONFIG["enabled"]:
            self.sns_client = boto3.client(
                'sns',
                region_name=AWS_SNS_CONFIG["region"],
                aws_access_key_id=AWS_SNS_CONFIG["access_key"],
                aws_secret_access_key=AWS_SNS_CONFIG["secret_key"]
            )

    async def add_alert(self, title: str, message: str, severity: str = "info") -> None:
        """Add a new alert with optional AI analysis"""
        alert = {
            "timestamp": datetime.utcnow(),
            "title": title,
            "message": message,
            "severity": severity
        }
        
        # Add AI analysis if enabled
        if self.ai_analyzer:
            analysis = await self.ai_analyzer.analyze_metrics(
                self._get_current_metrics(),
                self.alerts[-5:] if self.alerts else []
            )
            alert["ai_analysis"] = analysis
        
        self.alerts.append(alert)
        
        # Notify via SNS if enabled and alert is warning or higher
        if self.sns_client and severity in ["warning", "danger"]:
            await self._send_sns_notification(alert)

    async def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts with AI insights"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in self.alerts 
            if alert["timestamp"] >= cutoff_time
        ]
        
        # Add AI analysis for the overall alert state if enabled
        if self.ai_analyzer and recent_alerts:
            analysis = await self.ai_analyzer.analyze_metrics(
                self._get_current_metrics(),
                recent_alerts
            )
            
            # Add AI insights to the response
            return {
                "alerts": recent_alerts,
                "ai_insights": {
                    "analysis": analysis["analysis"],
                    "recommendations": analysis["recommendations"],
                    "severity": analysis["severity"]
                }
            }
        
        return {"alerts": recent_alerts}

    def _get_current_metrics(self) -> Dict:
        """Get current system metrics for AI analysis"""
        # This would be replaced with actual metric collection
        return {
            "response_times": [100, 120, 150],  # Example values
            "error_rates": [1.5, 2.0, 2.5],     # Example values
            "request_rate": 100                  # Example value
        }

    async def _send_sns_notification(self, alert: Dict) -> None:
        """Send alert notification via AWS SNS"""
        if not self.sns_client:
            return
        
        try:
            message = f"""
Alert: {alert['title']}
Severity: {alert['severity']}
Message: {alert['message']}
Timestamp: {alert['timestamp']}
"""
            
            # Add AI analysis if available
            if "ai_analysis" in alert:
                message += f"""
AI Analysis:
{alert['ai_analysis']['analysis']}

Recommendations:
{chr(10).join('- ' + r for r in alert['ai_analysis']['recommendations'])}
"""
            
            await asyncio.to_thread(
                self.sns_client.publish,
                TopicArn=AWS_SNS_CONFIG["topic_arn"],
                Subject=f"API Alert: {alert['title']}",
                Message=message
            )
        
        except Exception as e:
            print(f"Failed to send SNS notification: {e}")
