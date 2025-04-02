import asyncio
import numpy as np
from typing import Dict, List
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from src.storage.database import Database
from src.alerts.alert_manager import AlertManager

class Predictor:
    def __init__(self):
        self.db = Database()
        self.alert_manager = AlertManager()
        self.model = RandomForestRegressor(n_estimators=100)
        self.running = False
        self.prediction_window = 3600  # 1 hour prediction window

    async def start(self):
        """Start the prediction process"""
        self.running = True
        await self._train_initial_model()
        asyncio.create_task(self._predict_issues())

    async def stop(self):
        """Stop the prediction process"""
        self.running = False

    async def _train_initial_model(self):
        """Train the initial prediction model using historical data"""
        historical_data = await self.db.get_historical_metrics()
        X, y = self._prepare_training_data(historical_data)
        if len(X) > 0:
            self.model.fit(X, y)

    def _prepare_training_data(self, data: Dict) -> tuple:
        """Prepare training data from historical metrics"""
        X = []
        y = []
        
        for service, metrics in data.items():
            for i in range(len(metrics["timestamps"]) - 6):
                # Features: last 5 measurements of response time, error rate, and load
                feature_vector = []
                for j in range(5):
                    feature_vector.extend([
                        metrics["response_times"][i + j],
                        metrics["error_rates"][i + j],
                        metrics["request_rates"][i + j]
                    ])
                X.append(feature_vector)
                
                # Target: whether an incident occurred in next hour
                y.append(1 if any(metrics["incidents"][i+5:i+6]) else 0)
        
        return np.array(X), np.array(y)

    async def _predict_issues(self):
        """Continuously predict potential issues"""
        while self.running:
            try:
                current_metrics = await self.db.get_recent_metrics()
                predictions = self._make_predictions(current_metrics)
                await self._handle_predictions(predictions)
                
                # Retrain model periodically with new data
                if datetime.now().minute == 0:  # Retrain every hour
                    await self._train_initial_model()
                    
            except Exception as e:
                print(f"Error in prediction: {e}")
            
            await asyncio.sleep(300)  # Predict every 5 minutes

    def _make_predictions(self, current_metrics: Dict) -> List[Dict]:
        """Make predictions based on current metrics"""
        predictions = []
        for service, metrics in current_metrics.items():
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(metrics)
            
            # Make prediction
            if len(feature_vector) > 0:
                probability = self.model.predict_proba([feature_vector])[0][1]
                if probability > 0.7:  # High probability threshold
                    predictions.append({
                        "service": service,
                        "probability": probability,
                        "predicted_time": datetime.now() + timedelta(hours=1),
                        "contributing_factors": self._identify_contributing_factors(metrics)
                    })
        
        return predictions

    def _prepare_feature_vector(self, metrics: Dict) -> List:
        """Prepare feature vector from current metrics"""
        feature_vector = []
        required_metrics = ["response_times", "error_rates", "request_rates"]
        
        # Ensure we have enough historical data
        if all(len(metrics[m]) >= 5 for m in required_metrics):
            for metric in required_metrics:
                feature_vector.extend(metrics[metric][-5:])  # Last 5 measurements
                
        return feature_vector

    def _identify_contributing_factors(self, metrics: Dict) -> List[str]:
        """Identify factors contributing to potential issues"""
        factors = []
        
        # Analyze response time trend
        if np.mean(metrics["response_times"][-5:]) > np.mean(metrics["response_times"][:-5]):
            factors.append("Increasing response time trend")
            
        # Analyze error rate
        if np.mean(metrics["error_rates"][-5:]) > 0.05:
            factors.append("Elevated error rate")
            
        # Analyze request rate
        if np.mean(metrics["request_rates"][-5:]) > np.percentile(metrics["request_rates"], 90):
            factors.append("High request volume")
            
        return factors

    async def _handle_predictions(self, predictions: List[Dict]):
        """Handle predictions and send alerts if necessary"""
        for prediction in predictions:
            await self.alert_manager.send_alert(
                title=f"Potential Issue Predicted for {prediction['service']}",
                message=f"Predicted issue within next hour (confidence: {prediction['probability']:.2%})\n"
                        f"Contributing factors:\n" + "\n".join(prediction['contributing_factors']),
                severity="warning"
            )
