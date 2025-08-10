# Testing Standards - TEP Industrial Intelligence Platform

## 🎯 **Testing Philosophy**

Industrial systems require **99.9% reliability**. Our testing strategy prioritizes:
1. **Safety-Critical Functions** - Fault detection and emergency controls
2. **Real-time Performance** - Sub-second response times
3. **Data Integrity** - Accurate sensor readings and calculations
4. **System Resilience** - Graceful degradation under failure

## 🏗️ **Testing Pyramid**

```
    /\     E2E Tests (10%)
   /  \    - Critical user workflows
  /____\   - Cross-service integration
 /      \  
/________\  Integration Tests (20%)
           - API contracts
           - Database interactions
           - Service communication

Unit Tests (70%)
- Pure functions
- Component logic
- Business rules
```

## 🧪 **Unit Testing Standards**

### **Frontend (React + TypeScript)**
```typescript
// Component testing with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { TEPControlPanel } from './TEPControlPanel';

describe('TEPControlPanel', () => {
  it('should start simulation when start button clicked', async () => {
    const mockStartSimulation = jest.fn();
    render(<TEPControlPanel onStart={mockStartSimulation} />);
    
    const startButton = screen.getByRole('button', { name: /start simulation/i });
    fireEvent.click(startButton);
    
    expect(mockStartSimulation).toHaveBeenCalledWith({
      preset: 'demo',
      duration: 1000
    });
  });

  it('should display anomaly alert when anomaly detected', () => {
    render(<TEPControlPanel anomalyScore={2.5} threshold={2.0} />);
    
    expect(screen.getByText(/anomaly detected/i)).toBeInTheDocument();
    expect(screen.getByText(/score: 2.5/i)).toBeInTheDocument();
  });
});
```

### **Backend (Python + FastAPI)**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.tep_simulator import TEPSimulator

client = TestClient(app)

class TestTEPSimulation:
    def test_start_simulation_success(self):
        response = client.post("/api/v1/simulation/start", json={
            "duration": 100,
            "preset": "demo",
            "faults": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "simulation_id" in data["data"]

    def test_simulation_with_fault_injection(self):
        response = client.post("/api/v1/simulation/start", json={
            "duration": 100,
            "faults": {
                "idv1": {"start_time": 50, "magnitude": 0.5}
            }
        })
        
        assert response.status_code == 200
        # Verify fault is properly configured
        simulation_data = response.json()["data"]
        assert simulation_data["faults"]["idv1"]["magnitude"] == 0.5

    @pytest.mark.parametrize("invalid_input,expected_error", [
        ({"duration": -1}, "Duration must be positive"),
        ({"duration": 10000}, "Duration exceeds maximum"),
        ({"faults": {"idv25": {}}}, "Invalid fault ID")
    ])
    def test_validation_errors(self, invalid_input, expected_error):
        response = client.post("/api/v1/simulation/start", json=invalid_input)
        
        assert response.status_code == 422
        assert expected_error in response.json()["error"]["message"]
```

## 🔗 **Integration Testing**

### **API Contract Testing**
```python
def test_simulation_to_anomaly_detection_flow():
    # Start simulation
    sim_response = client.post("/api/v1/simulation/start", json={
        "duration": 50,
        "preset": "demo"
    })
    simulation_id = sim_response.json()["data"]["simulation_id"]
    
    # Wait for data generation
    time.sleep(2)
    
    # Check anomaly detection receives data
    anomaly_response = client.get(f"/api/v1/anomaly/status/{simulation_id}")
    
    assert anomaly_response.status_code == 200
    anomaly_data = anomaly_response.json()["data"]
    assert "anomaly_score" in anomaly_data
    assert "variables" in anomaly_data
```

### **Database Integration**
```python
def test_historical_data_storage():
    # Generate simulation data
    simulator = TEPSimulator()
    data = simulator.run_simulation(duration=10)
    
    # Store in database
    db_service = DatabaseService()
    db_service.store_simulation_data(data)
    
    # Verify retrieval
    retrieved_data = db_service.get_simulation_data(
        start_time=data[0]["timestamp"],
        end_time=data[-1]["timestamp"]
    )
    
    assert len(retrieved_data) == len(data)
    assert retrieved_data[0]["xmeas_1"] == data[0]["xmeas_1"]
```

## 🌐 **End-to-End Testing**

### **Critical User Workflows**
```typescript
// Playwright E2E test
import { test, expect } from '@playwright/test';

test('Complete fault detection workflow', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('http://localhost:3000');
  
  // Start simulation
  await page.click('[data-testid="start-simulation"]');
  await page.selectOption('[data-testid="preset-select"]', 'demo');
  await page.click('[data-testid="confirm-start"]');
  
  // Verify simulation is running
  await expect(page.locator('[data-testid="simulation-status"]')).toContainText('Running');
  
  // Inject fault
  await page.fill('[data-testid="idv1-slider"]', '0.5');
  await page.click('[data-testid="apply-fault"]');
  
  // Wait for anomaly detection
  await page.waitForSelector('[data-testid="anomaly-alert"]', { timeout: 30000 });
  
  // Verify LLM analysis is triggered
  await expect(page.locator('[data-testid="llm-analysis"]')).toBeVisible();
  
  // Check analysis results
  await page.waitForSelector('[data-testid="analysis-complete"]', { timeout: 60000 });
  const analysisText = await page.textContent('[data-testid="analysis-result"]');
  expect(analysisText).toContain('fault detected');
});
```

## ⚡ **Performance Testing**

### **Load Testing with Locust**
```python
from locust import HttpUser, task, between

class TEPPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Authenticate user
        response = self.client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_simulation_status(self):
        self.client.get("/api/v1/simulation/status")
    
    @task(1)
    def start_simulation(self):
        self.client.post("/api/v1/simulation/start", json={
            "duration": 100,
            "preset": "demo"
        })
    
    @task(2)
    def get_anomaly_data(self):
        self.client.get("/api/v1/anomaly/current")
```

### **Performance Benchmarks**
```python
import pytest
import time

def test_simulation_startup_performance():
    start_time = time.time()
    
    response = client.post("/api/v1/simulation/start", json={
        "duration": 1000,
        "preset": "balanced"
    })
    
    end_time = time.time()
    startup_time = end_time - start_time
    
    assert response.status_code == 200
    assert startup_time < 2.0  # Must start within 2 seconds

def test_real_time_data_latency():
    # Measure WebSocket data latency
    import websocket
    
    latencies = []
    
    def on_message(ws, message):
        receive_time = time.time()
        data = json.loads(message)
        send_time = data["timestamp"]
        latency = receive_time - send_time
        latencies.append(latency)
    
    ws = websocket.WebSocketApp("ws://localhost:8000/ws/realtime",
                               on_message=on_message)
    
    # Collect data for 30 seconds
    ws.run_forever()
    
    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 0.1  # Average latency < 100ms
```

## 🔒 **Security Testing**

### **Authentication Testing**
```python
def test_unauthorized_access():
    response = client.get("/api/v1/simulation/status")
    assert response.status_code == 401

def test_insufficient_permissions():
    # Login as operator (limited permissions)
    token = get_operator_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access admin endpoint
    response = client.post("/api/v1/admin/users", 
                          headers=headers, 
                          json={"username": "new_user"})
    
    assert response.status_code == 403
```

### **Input Validation Testing**
```python
def test_sql_injection_protection():
    malicious_input = "'; DROP TABLE users; --"
    
    response = client.get(f"/api/v1/simulation/history?plant_id={malicious_input}")
    
    # Should return validation error, not execute SQL
    assert response.status_code == 422
    assert "Invalid plant ID format" in response.json()["error"]["message"]
```

## 📊 **Test Coverage Requirements**

### **Coverage Targets**
- **Unit Tests**: 90% line coverage minimum
- **Integration Tests**: 80% API endpoint coverage
- **E2E Tests**: 100% critical user workflow coverage

### **Coverage Reporting**
```bash
# Frontend coverage
npm run test:coverage
# Target: 90% statements, 85% branches, 90% functions

# Backend coverage
pytest --cov=app --cov-report=html
# Target: 90% line coverage, 85% branch coverage
```

## 🚨 **Test Data Management**

### **Test Data Strategy**
- **Unit Tests**: Mock data, no external dependencies
- **Integration Tests**: Test database with known datasets
- **E2E Tests**: Isolated test environment with realistic data

### **TEP Test Scenarios**
```python
# Standard test scenarios for TEP simulation
TEST_SCENARIOS = {
    "normal_operation": {
        "duration": 100,
        "faults": {},
        "expected_anomaly": False
    },
    "reactor_temperature_fault": {
        "duration": 200,
        "faults": {"idv1": {"start_time": 100, "magnitude": 0.8}},
        "expected_anomaly": True,
        "expected_detection_time": 120
    },
    "multiple_faults": {
        "duration": 300,
        "faults": {
            "idv1": {"start_time": 100, "magnitude": 0.5},
            "idv2": {"start_time": 200, "magnitude": 0.7}
        },
        "expected_anomaly": True
    }
}
```

## 🔄 **Continuous Testing**

### **CI/CD Pipeline Testing**
```yaml
# GitHub Actions workflow
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          npm test
          pytest tests/unit/
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
    steps:
      - name: Run integration tests
        run: pytest tests/integration/
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Start services
        run: docker-compose up -d
      - name: Run E2E tests
        run: npx playwright test
```

This comprehensive testing strategy ensures the TEP Industrial Intelligence Platform meets industrial reliability standards while maintaining development velocity.
