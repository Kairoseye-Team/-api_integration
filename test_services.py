"""
Test script for AWS SNS and Elasticsearch integration
"""
import asyncio
import sys
from datetime import datetime
from src.alerts.alert_manager import AlertManager
from src.collectors.log_collector import LogCollector
from src.config.external_services import AWS_SNS_CONFIG, ELASTICSEARCH_CONFIG

async def test_sns():
    """Test AWS SNS integration"""
    print("\n=== Testing AWS SNS ===")
    alert_manager = AlertManager()
    
    # Create a test alert
    test_alert = {
        "service": "test-service",
        "title": "Test Alert",
        "message": "This is a test alert",
        "severity": "info",
        "timestamp": datetime.utcnow()
    }
    
    # Try to send alert
    print(f"SNS Enabled: {AWS_SNS_CONFIG['enabled']}")
    print(f"SNS Topic ARN: {AWS_SNS_CONFIG['topic_arn']}")
    await alert_manager.create_alert(test_alert)
    
    print("If SNS is not configured, you should see the alert in console")

async def test_elasticsearch():
    """Test Elasticsearch integration"""
    print("\n=== Testing Elasticsearch ===")
    collector = LogCollector()
    
    # Try to initialize Elasticsearch
    print(f"Elasticsearch Enabled: {ELASTICSEARCH_CONFIG['enabled']}")
    print(f"Elasticsearch Host: {ELASTICSEARCH_CONFIG['hosts'][0]}")
    
    # Start collector
    await collector.start()
    print("Generating test logs...")
    
    # Wait for some logs to be generated
    await asyncio.sleep(10)
    
    # Stop collector
    await collector.stop()
    print("Log collection stopped")
    
    print("If Elasticsearch is not configured, logs are stored in memory")

async def main():
    """Run all tests"""
    print("Starting service tests...")
    
    try:
        # Test AWS SNS
        await test_sns()
        
        # Test Elasticsearch
        await test_elasticsearch()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)
    
    print("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main())
