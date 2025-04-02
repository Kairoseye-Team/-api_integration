import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List
from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as es_exceptions
from src.storage.database import Database
from src.config.external_services import ELASTICSEARCH_CONFIG

class LogCollector:
    def __init__(self):
        self.db = Database()
        self.running = False
        
        # Initialize Elasticsearch client
        self.es_client = None
        if ELASTICSEARCH_CONFIG["enabled"]:
            try:
                self.es_client = AsyncElasticsearch(
                    ELASTICSEARCH_CONFIG["hosts"],
                    basic_auth=(
                        ELASTICSEARCH_CONFIG["username"],
                        ELASTICSEARCH_CONFIG["password"]
                    ) if ELASTICSEARCH_CONFIG["username"] else None
                )
                print("Elasticsearch client initialized successfully")
            except es_exceptions.ElasticsearchException as e:
                print(f"Failed to initialize Elasticsearch client: {e}")
                if ELASTICSEARCH_CONFIG["fallback_to_memory"]:
                    print("Falling back to in-memory storage")
        
        # Define services and their endpoints
        self.services = {
            "api-gateway": {
                "endpoints": [
                    "/auth",
                    "/users",
                    "/products",
                    "/orders"
                ],
                "expected_latency": 50  # base latency in ms
            },
            "auth-service": {
                "endpoints": [
                    "/login",
                    "/register",
                    "/verify",
                    "/reset-password"
                ],
                "expected_latency": 100
            },
            "user-service": {
                "endpoints": [
                    "/profile",
                    "/preferences",
                    "/notifications",
                    "/settings"
                ],
                "expected_latency": 150
            },
            "product-service": {
                "endpoints": [
                    "/catalog",
                    "/inventory",
                    "/pricing",
                    "/categories"
                ],
                "expected_latency": 200
            },
            "order-service": {
                "endpoints": [
                    "/create",
                    "/status",
                    "/history",
                    "/payment"
                ],
                "expected_latency": 250
            }
        }

    async def start(self):
        """Start the log collection process"""
        self.running = True
        if self.es_client:
            try:
                # Create index if it doesn't exist
                index_name = f"{ELASTICSEARCH_CONFIG['index_prefix']}-{datetime.utcnow().strftime('%Y-%m')}"
                if not await self.es_client.indices.exists(index=index_name):
                    await self.es_client.indices.create(
                        index=index_name,
                        mappings={
                            "properties": {
                                "timestamp": {"type": "date"},
                                "service": {"type": "keyword"},
                                "endpoint": {"type": "keyword"},
                                "response_time": {"type": "float"},
                                "status_code": {"type": "integer"},
                                "error": {"type": "boolean"},
                                "error_type": {"type": "keyword"},
                                "environment": {"type": "keyword"},
                                "region": {"type": "keyword"},
                                "request_id": {"type": "keyword"},
                                "user_id": {"type": "keyword"},
                                "method": {"type": "keyword"},
                                "response_size": {"type": "integer"}
                            }
                        }
                    )
                print(f"Elasticsearch index '{index_name}' ready")
            except es_exceptions.ElasticsearchException as e:
                print(f"Failed to create Elasticsearch index: {e}")
                self.es_client = None
                if ELASTICSEARCH_CONFIG["fallback_to_memory"]:
                    print("Falling back to in-memory storage")
        
        # Generate initial sample data
        await self._generate_sample_logs()
        
        asyncio.create_task(self._collect_logs())

    async def stop(self):
        """Stop the log collection process"""
        self.running = False
        if self.es_client:
            await self.es_client.close()

    async def _generate_sample_logs(self):
        """Generate sample logs for testing"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        sample_logs = []
        
        # Generate logs for the last hour
        current_time = hour_ago
        while current_time <= now:
            # Generate 10-20 logs per minute
            for _ in range(random.randint(10, 20)):
                service = random.choice(list(self.services.keys()))
                endpoint = random.choice(self.services[service]["endpoints"])
                base_latency = self.services[service]["expected_latency"]
                
                # Simulate occasional high latency and errors
                is_error = random.random() < 0.05  # 5% error rate
                latency_multiplier = random.uniform(0.8, 3.0 if is_error else 1.2)
                
                log = {
                    "timestamp": current_time,
                    "service": service,
                    "endpoint": endpoint,
                    "response_time": base_latency * latency_multiplier,
                    "error": is_error,
                    "status_code": 500 if is_error else 200
                }
                sample_logs.append(log)
            
            current_time += timedelta(minutes=1)
        
        # Store sample logs
        await self.db.store_logs(sample_logs)
        print(f"Generated {len(sample_logs)} sample logs")

    async def _store_logs(self, logs: List[Dict]):
        """Store logs in Elasticsearch or fallback to memory"""
        if self.es_client:
            try:
                index_name = f"{ELASTICSEARCH_CONFIG['index_prefix']}-{datetime.utcnow().strftime('%Y-%m')}"
                # Bulk index logs to Elasticsearch
                body = []
                for log in logs:
                    body.extend([
                        {"index": {"_index": index_name}},
                        log
                    ])
                if body:
                    await self.es_client.bulk(operations=body, refresh=True)
                return
            except es_exceptions.ElasticsearchException as e:
                print(f"Failed to store logs in Elasticsearch: {e}")
        
        # Fallback to in-memory storage
        if ELASTICSEARCH_CONFIG["fallback_to_memory"]:
            await self.db.store_logs(logs)

    async def _collect_logs(self):
        """Generate and store logs"""
        while self.running:
            try:
                # Generate new logs
                service = random.choice(list(self.services.keys()))
                endpoint = random.choice(self.services[service]["endpoints"])
                base_latency = self.services[service]["expected_latency"]
                
                # Simulate occasional high latency and errors
                is_error = random.random() < 0.05  # 5% error rate
                latency_multiplier = random.uniform(0.8, 3.0 if is_error else 1.2)
                
                log = {
                    "timestamp": datetime.utcnow(),
                    "service": service,
                    "endpoint": endpoint,
                    "response_time": base_latency * latency_multiplier,
                    "error": is_error,
                    "status_code": 500 if is_error else 200
                }
                
                # Store log
                await self._store_logs([log])
                
            except Exception as e:
                print(f"Error collecting logs: {e}")
            
            # Wait before next collection
            await asyncio.sleep(5)  # Collect every 5 seconds
