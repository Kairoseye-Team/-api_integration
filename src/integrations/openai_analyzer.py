from typing import List, Dict
from openai import AsyncOpenAI
from datetime import datetime, timedelta

class OpenAIAnalyzer:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.system_prompt = """You are an AI system monitoring expert. Analyze the provided metrics and alerts to:
1. Identify potential issues and their root causes
2. Suggest actionable solutions
3. Predict possible future problems
4. Recommend preventive measures
Format your response in a clear, concise manner."""

    async def analyze_metrics(self, metrics: Dict, alerts: List[Dict]) -> Dict:
        """Analyze metrics and alerts using OpenAI"""
        try:
            # Prepare the context for OpenAI
            context = self._prepare_analysis_context(metrics, alerts)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and return the analysis
            analysis = response.choices[0].message.content
            
            # Structure the analysis
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": analysis,
                "recommendations": self._extract_recommendations(analysis),
                "severity": self._determine_severity(metrics, alerts)
            }
        
        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "analysis": "Failed to generate analysis",
                "recommendations": [],
                "severity": "warning"
            }

    def _prepare_analysis_context(self, metrics: Dict, alerts: List[Dict]) -> str:
        """Prepare context string for OpenAI analysis"""
        # Get the latest metrics
        latest_metrics = {
            "response_time": metrics["response_times"][-1] if metrics["response_times"] else 0,
            "error_rate": metrics["error_rates"][-1] if metrics["error_rates"] else 0,
            "request_rate": metrics["request_rate"]
        }
        
        # Format alerts
        recent_alerts = "\n".join([
            f"- {alert['title']}: {alert['message']} ({alert['severity']})"
            for alert in alerts[-5:] # Last 5 alerts
        ])
        
        return f"""
Current System Metrics:
- Response Time: {latest_metrics['response_time']}ms
- Error Rate: {latest_metrics['error_rate']}%
- Request Rate: {latest_metrics['request_rate']}/min

Recent Alerts:
{recent_alerts}

Please analyze these metrics and alerts to:
1. Identify any potential issues
2. Suggest immediate actions
3. Recommend preventive measures
"""

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract actionable recommendations from the analysis"""
        recommendations = []
        
        # Split analysis into lines and look for actionable items
        for line in analysis.split('\n'):
            if any(keyword in line.lower() for keyword in ['recommend', 'should', 'suggest', 'consider', 'try']):
                # Clean up the recommendation
                recommendation = line.strip('- ').strip()
                if recommendation:
                    recommendations.append(recommendation)
        
        return recommendations

    def _determine_severity(self, metrics: Dict, alerts: List[Dict]) -> str:
        """Determine the overall severity based on metrics and alerts"""
        if not metrics["error_rates"] or not metrics["response_times"]:
            return "info"
            
        latest_error_rate = metrics["error_rates"][-1]
        latest_response_time = metrics["response_times"][-1]
        
        # Check for critical conditions
        if latest_error_rate > 10 or latest_response_time > 1000:
            return "danger"
        # Check for warning conditions
        elif latest_error_rate > 5 or latest_response_time > 500:
            return "warning"
        # Everything looks good
        return "info"
