# API Standards - TEP Industrial Intelligence Platform

## 🎯 **RESTful API Conventions**

### **URL Structure**
```
/api/v1/{service}/{resource}/{id?}/{action?}

Examples:
GET    /api/v1/simulation/status
POST   /api/v1/simulation/start
PUT    /api/v1/simulation/config
GET    /api/v1/anomaly/detections
POST   /api/v1/llm/analyze
```

### **HTTP Methods**
- **GET**: Retrieve data (idempotent, cacheable)
- **POST**: Create resources or trigger actions
- **PUT**: Update entire resource (idempotent)
- **PATCH**: Partial resource updates
- **DELETE**: Remove resources

### **Status Codes**
- **200**: Success with response body
- **201**: Resource created successfully
- **204**: Success with no response body
- **400**: Bad request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Resource not found
- **409**: Conflict (resource already exists)
- **422**: Unprocessable entity (business logic error)
- **500**: Internal server error

## 📊 **Request/Response Format**

### **Request Headers**
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
X-Correlation-ID: {uuid}
X-Request-ID: {uuid}
```

### **Response Format**
```json
{
  "success": true,
  "data": {
    // Response payload
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "correlation_id": "uuid",
    "version": "v1"
  }
}
```

### **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "temperature",
        "message": "Value must be between -50 and 200"
      }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "correlation_id": "uuid"
  }
}
```

## 🏭 **TEP-Specific API Patterns**

### **Simulation Control**
```typescript
// Start simulation
POST /api/v1/simulation/start
{
  "duration": 1000,
  "faults": {
    "idv1": { "start_time": 100, "magnitude": 0.5 },
    "idv2": { "start_time": 200, "magnitude": 1.0 }
  },
  "preset": "balanced"
}

// Get current status
GET /api/v1/simulation/status
Response: {
  "data": {
    "status": "running",
    "current_step": 150,
    "total_steps": 1000,
    "variables": {
      "xmeas_1": 0.25,
      "xmeas_2": 3654.0,
      // ... all 52 variables
    },
    "anomaly_score": 1.2,
    "is_anomaly": false
  }
}
```

### **Real-time Data Streaming**
```typescript
// WebSocket connection
ws://localhost:8000/ws/realtime

// Message format
{
  "type": "tep_data",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "step": 150,
    "variables": { /* 52 TEP variables */ },
    "anomaly_score": 1.2,
    "is_anomaly": false
  }
}
```

### **Anomaly Detection**
```typescript
// Get anomaly status
GET /api/v1/anomaly/status
Response: {
  "data": {
    "current_score": 2.5,
    "threshold": 2.0,
    "is_anomaly": true,
    "detection_time": "2024-01-15T10:30:00Z",
    "contributing_variables": [
      { "name": "reactor_temperature", "contribution": 0.8 },
      { "name": "reactor_pressure", "contribution": 0.6 }
    ]
  }
}

// Trigger LLM analysis
POST /api/v1/llm/analyze
{
  "anomaly_data": {
    "variables": { /* top contributing variables */ },
    "context": "reactor_temperature_spike"
  },
  "providers": ["claude", "gemini", "local"]
}
```

## 🔒 **Authentication & Authorization**

### **JWT Token Structure**
```json
{
  "sub": "user_id",
  "role": "process_engineer",
  "permissions": [
    "simulation:read",
    "simulation:write",
    "anomaly:read",
    "llm:analyze"
  ],
  "plant_id": "plant_001",
  "exp": 1642248000
}
```

### **Role-Based Permissions**
- **plant_operator**: Read monitoring data, basic controls
- **process_engineer**: Full simulation control, analysis access
- **maintenance_engineer**: Historical data, predictive insights
- **plant_manager**: Dashboards, reports, user management
- **admin**: System configuration, user management

## 📈 **Pagination & Filtering**

### **Query Parameters**
```
GET /api/v1/anomaly/history?page=1&limit=50&start_date=2024-01-01&end_date=2024-01-31&severity=high

Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1250,
    "pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

## ⚡ **Performance Standards**

### **Response Time Targets**
- **Real-time data**: < 100ms
- **Simple queries**: < 500ms
- **Complex analysis**: < 2s
- **LLM analysis**: < 30s

### **Rate Limiting**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

### **Caching Headers**
```http
Cache-Control: public, max-age=300
ETag: "abc123"
Last-Modified: Mon, 15 Jan 2024 10:30:00 GMT
```

## 🔍 **Monitoring & Observability**

### **Health Check Endpoints**
```
GET /health
Response: {
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "llm_providers": "degraded"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Metrics Endpoints**
```
GET /metrics (Prometheus format)
# HELP tep_simulation_requests_total Total simulation requests
# TYPE tep_simulation_requests_total counter
tep_simulation_requests_total{method="POST",status="200"} 1234
```

## 🧪 **Testing Standards**

### **API Test Structure**
```python
def test_start_simulation_success():
    response = client.post("/api/v1/simulation/start", json={
        "duration": 100,
        "preset": "demo"
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "simulation_id" in response.json()["data"]
```

### **Contract Testing**
- OpenAPI schema validation
- Request/response format verification
- Error handling consistency
- Performance benchmarking

This API standard ensures consistent, reliable, and maintainable interfaces across all services in the TEP Industrial Intelligence Platform.
