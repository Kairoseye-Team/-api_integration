"""
Configuration settings for the API monitoring system
"""

# Service Configuration
SERVICES = {
    "api-gateway": {
        "endpoints": [
            "/auth",
            "/users",
            "/products",
            "/orders"
        ],
        "expected_latency": 50,  # Base latency in ms
        "error_threshold": 0.05  # 5% error rate threshold
    },
    "auth-service": {
        "endpoints": [
            "/login",
            "/register",
            "/verify",
            "/reset-password"
        ],
        "expected_latency": 100,
        "error_threshold": 0.03
    },
    "user-service": {
        "endpoints": [
            "/profile",
            "/preferences",
            "/notifications",
            "/settings"
        ],
        "expected_latency": 150,
        "error_threshold": 0.04
    },
    "product-service": {
        "endpoints": [
            "/catalog",
            "/inventory",
            "/pricing",
            "/categories"
        ],
        "expected_latency": 200,
        "error_threshold": 0.05
    },
    "order-service": {
        "endpoints": [
            "/create",
            "/status",
            "/history",
            "/payment"
        ],
        "expected_latency": 250,
        "error_threshold": 0.05
    }
}

# Monitoring Configuration
MONITORING = {
    "collection_interval": 5,  # Seconds between log collection
    "retention_period": 24,    # Hours to keep logs
    "business_hours": {
        "start": 9,           # 9 AM
        "end": 17            # 5 PM
    }
}

# Alert Configuration
ALERT_THRESHOLDS = {
    "response_time": {
        "critical": 1000,     # ms
        "warning": 500        # ms
    },
    "error_rate": {
        "critical": 0.10,     # 10%
        "warning": 0.05       # 5%
    },
    "request_rate": {
        "min": 1,            # requests per minute
        "max": 1000          # requests per minute
    }
}

ALERT_SETTINGS = {
    "cooldown_period": 300,   # 5 minutes between similar alerts
    "auto_acknowledge": 60,   # Minutes before auto-acknowledging
    "auto_resolve": 24,      # Hours before auto-resolving
}

# Demo Data Generation
DEMO_SETTINGS = {
    "regions": ["us-east", "us-west", "eu-central"],
    "environments": ["production", "staging"],
    "error_types": [
        "timeout",
        "validation_error",
        "database_error",
        "auth_error"
    ],
    "auth_types": ["basic", "oauth", "jwt"],
    "http_methods": ["GET", "POST", "PUT", "DELETE"],
    "response_size": {
        "min": 100,          # bytes
        "max": 10000         # bytes
    }
}

# Database Settings
DATABASE = {
    "type": "in-memory",     # or "mongodb"
    "mongodb_uri": "mongodb://localhost:27017",
    "database_name": "api_monitor"
}
