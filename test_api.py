import requests
import json

# Test data
data = {
    "metrics": {
        "response_times": [150, 200, 180],
        "error_rates": [0.02, 0.03, 0.01],
        "request_rate": 100
    },
    "alerts": [
        {
            "title": "High Latency",
            "message": "Response time exceeded threshold",
            "severity": "warning"
        }
    ]
}

# Make POST request to analyze endpoint
response = requests.post('http://127.0.0.1:8000/analyze', json=data)

# Pretty print the response
print(json.dumps(response.json(), indent=2))
