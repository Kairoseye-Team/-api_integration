"""
Configuration for external services (AWS SNS, Elasticsearch, and OpenAI)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_SNS_CONFIG = {
    "enabled": bool(os.getenv("AWS_ACCESS_KEY_ID")),  # Enable if credentials exist
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    "topic_arn": os.getenv("AWS_SNS_TOPIC_ARN", ""),
    "fallback_to_console": True
}

ELASTICSEARCH_CONFIG = {
    "enabled": bool(os.getenv("ELASTICSEARCH_HOST")),  # Enable if host exists
    "hosts": [os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")],
    "index_prefix": os.getenv("ELASTICSEARCH_INDEX_PREFIX", "api_monitor"),
    "username": os.getenv("ELASTICSEARCH_USERNAME", ""),
    "password": os.getenv("ELASTICSEARCH_PASSWORD", ""),
    "fallback_to_memory": True
}

OPENAI_CONFIG = {
    "enabled": os.getenv("OPENAI_ENABLED", "false").lower() == "true",
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "500"))
}

# Monitoring settings
MONITORING_CONFIG = {
    "alert_cooldown": int(os.getenv("ALERT_COOLDOWN", 300)),
    "log_retention_days": int(os.getenv("LOG_RETENTION_DAYS", 7)),
    "monitoring_interval": int(os.getenv("MONITORING_INTERVAL", 5))
}
