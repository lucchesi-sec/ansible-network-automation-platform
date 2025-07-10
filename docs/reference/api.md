# API Reference

## Overview

Complete API reference for the Ansible Cloud Playbook platform, including network automation APIs, AI/ML endpoints, and management interfaces.

## Authentication

All API endpoints require authentication using one of the following methods:

### API Key Authentication
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     https://api.example.com/v1/endpoint
```

### Bearer Token Authentication
```bash
curl -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     https://api.example.com/v1/endpoint
```

## Network Automation API

### Device Management

#### List Devices
```http
GET /api/v1/devices
```

**Response:**
```json
{
  "devices": [
    {
      "id": "router-core-01",
      "type": "cisco_router",
      "status": "active",
      "ip_address": "10.0.1.1",
      "role": "core_router",
      "last_seen": "2025-07-10T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

#### Get Device Details
```http
GET /api/v1/devices/{device_id}
```

**Response:**
```json
{
  "id": "router-core-01",
  "type": "cisco_router",
  "status": "active",
  "configuration": {
    "interfaces": [...],
    "routing": {...},
    "security": {...}
  },
  "metrics": {
    "cpu_utilization": 45.2,
    "memory_usage": 67.8,
    "interface_utilization": {...}
  }
}
```

#### Update Device Configuration
```http
PUT /api/v1/devices/{device_id}/configuration
Content-Type: application/json

{
  "configuration": {
    "interfaces": {
      "GigabitEthernet0/1": {
        "ip_address": "10.0.2.1/24",
        "description": "Updated interface",
        "status": "up"
      }
    }
  }
}
```

### Deployment Management

#### Trigger Deployment
```http
POST /api/v1/deployments
Content-Type: application/json

{
  "environment": "production",
  "playbook": "master_enterprise_deployment.yml",
  "inventory": "production.yml",
  "extra_vars": {
    "deploy_advanced_features": true
  },
  "dry_run": false
}
```

**Response:**
```json
{
  "deployment_id": "deploy-2025-07-10-001",
  "status": "running",
  "started_at": "2025-07-10T10:30:00Z",
  "estimated_duration": "45m",
  "progress": 15
}
```

#### Get Deployment Status
```http
GET /api/v1/deployments/{deployment_id}
```

**Response:**
```json
{
  "deployment_id": "deploy-2025-07-10-001",
  "status": "completed",
  "started_at": "2025-07-10T10:30:00Z",
  "completed_at": "2025-07-10T11:15:00Z",
  "duration": "45m12s",
  "progress": 100,
  "results": {
    "success": true,
    "devices_updated": 25,
    "tasks_executed": 450,
    "errors": []
  }
}
```

## AI/ML Platform API

### Model Management

#### List Models
```http
GET /api/v1/models
```

**Response:**
```json
{
  "models": [
    {
      "id": "network_anomaly_v1.2",
      "name": "Network Anomaly Detection",
      "version": "1.2.0",
      "status": "deployed",
      "accuracy": 0.95,
      "created_at": "2025-07-01T00:00:00Z"
    }
  ]
}
```

#### Get Model Predictions
```http
POST /api/v1/models/{model_id}/predict
Content-Type: application/json

{
  "features": {
    "cpu_utilization": 0.85,
    "memory_usage": 0.72,
    "bandwidth_utilization": 0.91,
    "error_rate": 0.02,
    "latency_ms": 15.5
  }
}
```

**Response:**
```json
{
  "prediction": {
    "anomaly_score": 0.87,
    "classification": "anomaly",
    "confidence": 0.92,
    "recommendations": [
      "Check CPU utilization on core routers",
      "Review recent configuration changes",
      "Monitor traffic patterns for DDoS indicators"
    ]
  },
  "model_version": "1.2.0",
  "timestamp": "2025-07-10T10:30:00Z"
}
```

#### Trigger Model Training
```http
POST /api/v1/models/train
Content-Type: application/json

{
  "model_type": "anomaly_detection",
  "dataset_version": "v2.1",
  "hyperparameters": {
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32
  },
  "schedule": "immediate"
}
```

### Analytics API

#### Network Health Metrics
```http
GET /api/v1/analytics/network-health
```

**Response:**
```json
{
  "overall_health": 95.2,
  "metrics": {
    "availability": 99.8,
    "performance": 92.1,
    "security": 96.5,
    "capacity": 87.3
  },
  "alerts": {
    "critical": 0,
    "warning": 3,
    "info": 12
  },
  "timestamp": "2025-07-10T10:30:00Z"
}
```

#### Performance Trends
```http
GET /api/v1/analytics/performance?period=24h&metric=latency
```

**Response:**
```json
{
  "metric": "latency",
  "period": "24h",
  "data_points": [
    {
      "timestamp": "2025-07-09T10:30:00Z",
      "value": 12.5,
      "unit": "ms"
    }
  ],
  "statistics": {
    "min": 8.2,
    "max": 45.6,
    "avg": 15.3,
    "std_dev": 5.7
  }
}
```

## Security API

### Access Control

#### List Users
```http
GET /api/v1/users
```

#### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "username": "jdoe",
  "email": "john.doe@company.com",
  "role": "network_operator",
  "permissions": [
    "devices:read",
    "deployments:create",
    "analytics:read"
  ]
}
```

### Audit Logs

#### Get Audit Logs
```http
GET /api/v1/audit/logs?start_date=2025-07-09&end_date=2025-07-10
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-07-10T10:30:00Z",
      "user": "admin",
      "action": "device.configuration.update",
      "resource": "router-core-01",
      "result": "success",
      "ip_address": "10.0.1.100"
    }
  ],
  "total": 150,
  "page": 1
}
```

## Monitoring API

### Metrics Collection

#### Device Metrics
```http
GET /api/v1/metrics/devices/{device_id}?metric=cpu&period=1h
```

#### System Metrics
```http
GET /api/v1/metrics/system?metrics=cpu,memory,disk&resolution=5m
```

### Alerting

#### List Alerts
```http
GET /api/v1/alerts?status=active&severity=warning
```

#### Create Alert Rule
```http
POST /api/v1/alerts/rules
Content-Type: application/json

{
  "name": "High CPU Usage",
  "condition": "cpu_utilization > 90",
  "duration": "5m",
  "severity": "warning",
  "actions": [
    {
      "type": "email",
      "recipients": ["admin@company.com"]
    }
  ]
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "cpu_utilization",
      "reason": "Value must be between 0 and 1"
    }
  },
  "timestamp": "2025-07-10T10:30:00Z",
  "request_id": "req-12345"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 422  | Validation Error |
| 500  | Internal Server Error |
| 503  | Service Unavailable |

## Rate Limiting

API requests are rate limited:
- **Free tier**: 1,000 requests/hour
- **Professional**: 10,000 requests/hour
- **Enterprise**: 100,000 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 750
X-RateLimit-Reset: 1625097600
```

## SDKs and Libraries

### Python SDK
```python
from ansible_cloud_api import Client

client = Client(api_key="your-api-key")
devices = client.devices.list()
deployment = client.deployments.create(
    environment="production",
    playbook="master_enterprise_deployment.yml"
)
```

### JavaScript SDK
```javascript
import { AnsibeCloudAPI } from '@ansible-cloud/api';

const client = new AnsibeCloudAPI({ apiKey: 'your-api-key' });
const devices = await client.devices.list();
const prediction = await client.models.predict('anomaly_v1.2', features);
```

---

For more detailed examples and advanced usage, see the [Integration Guide](../guides/api-integration.md).