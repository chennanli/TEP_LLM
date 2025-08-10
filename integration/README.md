# 🏭 TEP Industrial Intelligence Platform

## 🎯 **Overview**

A production-ready industrial intelligence platform that combines real-time Tennessee Eastman Process (TEP) simulation, AI-powered fault diagnosis, and process optimization in a unified dashboard.

## ✨ **Key Features**

- **🎛️ Unified Control Panel** - Single interface for all operations
- **📊 Real-time Monitoring** - Live process data with 3-second updates
- **🤖 AI-Powered Analysis** - Multi-LLM fault diagnosis (Claude, Gemini, Local)
- **🔍 Anomaly Detection** - PCA-based fault detection with visual indicators
- **📈 Historical Analysis** - Fault pattern tracking and trend analysis
- **🏗️ Microservices Architecture** - Scalable, maintainable, containerized

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

### **Development Setup**
```bash
# Clone and setup
git clone <repository-url>
cd tep-industrial-intelligence

# Start all services
make dev-up

# Access the platform
open http://localhost:3000
```

### **Production Deployment**
```bash
# Build and deploy
make prod-deploy

# Monitor services
make logs
```

## 🏗️ **Architecture**

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   React Frontend    │    │   FastAPI Gateway   │    │   Core Services     │
│   (Port 3000)       │◄──►│   (Port 8000)       │◄──►│   - TEP Simulator   │
│                     │    │                     │    │   - Anomaly Detect  │
│ • Control Panel     │    │ • Service Routing   │    │   - LLM Analysis    │
│ • Real-time Charts  │    │ • WebSocket Hub     │    │   - Optimization    │
│ • AI Analysis UI    │    │ • Authentication    │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │
                           ┌─────────────────────┐
                           │   Data Layer        │
                           │                     │
                           │ • PostgreSQL        │
                           │ • Redis Cache       │
                           │ • TDengine (TSDB)   │
                           │ • Vector DB (RAG)   │
                           └─────────────────────┘
```

## 📁 **Project Structure**

```
tep-industrial-intelligence/
├── .augment/steering/          # AI development guidance
├── src/
│   ├── frontend/               # React dashboard
│   └── backend/
│       ├── api-gateway/        # FastAPI gateway
│       └── services/           # Microservices
├── docs/                       # Documentation
├── tests/                      # Test suites
├── infrastructure/             # Deployment configs
└── docker-compose.yml          # Local development
```

## 🎛️ **Services**

### **Frontend Dashboard (Port 3000)**
- **Control Panel** - TEP simulation control and fault injection
- **Monitoring** - Real-time process visualization
- **Analysis** - AI-powered fault diagnosis
- **History** - Historical fault patterns and trends

### **API Gateway (Port 8000)**
- **Service Orchestration** - Route requests to appropriate services
- **WebSocket Hub** - Real-time data streaming
- **Authentication** - JWT-based security
- **Rate Limiting** - API protection

### **TEP Simulation Service (Port 8001)**
- **Dynamic Simulation** - Tennessee Eastman Process modeling
- **Fault Injection** - IDV parameter control
- **Data Generation** - 52 process variables
- **Anomaly Detection** - PCA-based fault detection

### **LLM Analysis Service (Port 8002)**
- **Multi-LLM Support** - Claude, Gemini, Local models
- **RAG System** - Chemical engineering knowledge base
- **Structured Analysis** - Consistent fault explanations
- **Provider Fallback** - Automatic failover

## 🔧 **Development Commands**

```bash
# Development
make dev-up          # Start all services
make dev-down        # Stop all services
make dev-logs        # View service logs
make dev-shell       # Access service shell

# Testing
make test-unit       # Run unit tests
make test-integration # Run integration tests
make test-e2e        # Run end-to-end tests
make test-all        # Run all tests

# Code Quality
make lint            # Run linters
make format          # Format code
make type-check      # TypeScript/mypy checks

# Database
make db-migrate      # Run database migrations
make db-seed         # Seed test data
make db-reset        # Reset database
```

## 📊 **Monitoring & Observability**

- **Health Checks**: `/health` endpoints for all services
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured JSON logs with correlation IDs
- **Tracing**: Jaeger distributed tracing
- **Dashboards**: Grafana monitoring dashboards

## 🔒 **Security**

- **Authentication**: JWT tokens with role-based access
- **Authorization**: Fine-grained permissions
- **Data Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Network Security**: VPN access, firewall rules
- **Audit Logging**: All user actions tracked

## 🎯 **Performance**

- **Response Time**: <2s for dashboard updates
- **Throughput**: 1000+ sensor readings/second
- **Availability**: 99.9% uptime target
- **Scalability**: Horizontal scaling support

## 📚 **Documentation**

- **[Architecture Guide](docs/architecture/)** - System design and patterns
- **[API Documentation](docs/api/)** - RESTful API reference
- **[User Manual](docs/user-guides/)** - Feature documentation
- **[Development Guide](docs/development/)** - Setup and contribution

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/tep-industrial-intelligence/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/tep-industrial-intelligence/discussions)

---

**Built with ❤️ for industrial process monitoring and AI-powered fault diagnosis**

## 📁 **Repository Structure**

This integration system is part of a larger repository:
- `../legacy/` - Original working POC system
- `../docs/` - Shared documentation and migration guides
- `../scripts/` - Shared utilities and tools

See `../docs/migration/migration-strategy.md` for the complete migration plan.
