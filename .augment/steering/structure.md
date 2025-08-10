# Project Structure - TEP Industrial Intelligence Platform

## 📁 **Root Directory Organization**

```
tep-industrial-intelligence/
├── .augment/                    # Augment Code steering documents
├── docs/                        # All documentation
├── src/                         # Source code
├── config/                      # Configuration files
├── scripts/                     # Automation scripts
├── tests/                       # Test suites
├── data/                        # Data files and models
├── infrastructure/              # Deployment configs
├── docker-compose.yml           # Local development
├── Makefile                     # Common commands
└── README.md                    # Project overview
```

## 🎯 **Naming Conventions**

### **Files & Directories**
- **Directories**: `kebab-case` (e.g., `anomaly-detection`, `llm-analysis`)
- **Python Files**: `snake_case` (e.g., `tep_simulator.py`, `anomaly_detector.py`)
- **TypeScript Files**: `PascalCase` for components, `camelCase` for utilities
- **Config Files**: `kebab-case.yml` (e.g., `docker-compose.yml`, `api-config.yml`)

### **Code Naming**
- **Classes**: `PascalCase` (e.g., `TEPSimulator`, `AnomalyDetector`)
- **Functions/Methods**: `snake_case` (Python), `camelCase` (TypeScript)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_SENSOR_COUNT`, `DEFAULT_TIMEOUT`)
- **Environment Variables**: `UPPER_SNAKE_CASE` with service prefix (e.g., `TEP_API_KEY`)

## 🎨 **Frontend Structure**

```
src/frontend/
├── public/                      # Static assets
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── common/              # Generic components (Button, Modal)
│   │   ├── charts/              # Process visualization components
│   │   ├── control-panel/       # TEP control components
│   │   ├── monitoring/          # Real-time monitoring components
│   │   └── analysis/            # LLM analysis components
│   ├── pages/                   # Route-level components
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── ProcessMonitoring.tsx
│   │   ├── FaultAnalysis.tsx
│   │   └── SystemConfiguration.tsx
│   ├── hooks/                   # Custom React hooks
│   │   ├── useWebSocket.ts      # Real-time data connection
│   │   ├── useTEPSimulation.ts  # TEP simulation state
│   │   └── useAnomalyDetection.ts
│   ├── services/                # API communication
│   │   ├── api.ts               # Base API client
│   │   ├── tepService.ts        # TEP simulation APIs
│   │   └── llmService.ts        # LLM analysis APIs
│   ├── types/                   # TypeScript type definitions
│   │   ├── tep.ts               # TEP-specific types
│   │   ├── anomaly.ts           # Anomaly detection types
│   │   └── api.ts               # API response types
│   ├── utils/                   # Utility functions
│   │   ├── dataProcessing.ts    # Data transformation
│   │   ├── chartHelpers.ts      # Chart configuration
│   │   └── validation.ts        # Input validation
│   ├── stores/                  # Zustand state management
│   │   ├── simulationStore.ts   # TEP simulation state
│   │   ├── anomalyStore.ts      # Anomaly detection state
│   │   └── uiStore.ts           # UI state (modals, notifications)
│   └── styles/                  # Global styles and themes
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

## ⚙️ **Backend Structure**

```
src/backend/
├── api-gateway/                 # FastAPI gateway service
│   ├── app/
│   │   ├── routers/             # API route definitions
│   │   │   ├── simulation.py    # TEP simulation endpoints
│   │   │   ├── anomaly.py       # Anomaly detection endpoints
│   │   │   └── llm.py           # LLM analysis endpoints
│   │   ├── middleware/          # Custom middleware
│   │   │   ├── auth.py          # Authentication middleware
│   │   │   ├── cors.py          # CORS configuration
│   │   │   └── logging.py       # Request logging
│   │   ├── models/              # Pydantic models
│   │   │   ├── tep.py           # TEP data models
│   │   │   ├── anomaly.py       # Anomaly detection models
│   │   │   └── responses.py     # API response models
│   │   └── main.py              # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── services/
│   ├── simulation/              # TEP simulation service
│   │   ├── app/
│   │   │   ├── core/            # Core simulation logic
│   │   │   │   ├── tep_simulator.py
│   │   │   │   ├── fault_injector.py
│   │   │   │   └── data_generator.py
│   │   │   ├── models/          # Data models
│   │   │   ├── api/             # Service API endpoints
│   │   │   └── main.py
│   │   └── Dockerfile
│   ├── anomaly-detection/       # ML-based anomaly detection
│   │   ├── app/
│   │   │   ├── models/          # ML model implementations
│   │   │   │   ├── pca_detector.py
│   │   │   │   ├── isolation_forest.py
│   │   │   │   └── autoencoder.py
│   │   │   ├── registry/        # Model registry and versioning
│   │   │   ├── training/        # Model training scripts
│   │   │   └── main.py
│   │   └── Dockerfile
│   └── llm-analysis/            # LLM-powered fault analysis
│       ├── app/
│       │   ├── providers/       # LLM provider implementations
│       │   │   ├── anthropic_client.py
│       │   │   ├── openai_client.py
│       │   │   └── local_client.py
│       │   ├── rag/             # RAG system components
│       │   │   ├── knowledge_base.py
│       │   │   ├── embeddings.py
│       │   │   └── retrieval.py
│       │   ├── prompts/         # Structured prompt templates
│       │   └── main.py
│       └── Dockerfile
└── shared/                      # Shared libraries
    ├── database/                # Database connections and models
    ├── messaging/               # Inter-service communication
    ├── monitoring/              # Logging and metrics
    └── utils/                   # Common utilities
```

## 📚 **Documentation Structure**

```
docs/
├── requirements/                # Product requirements
│   ├── PRD.md                   # Product Requirements Document
│   ├── user-stories.md          # Detailed user stories
│   └── technical-requirements.md
├── architecture/                # System design
│   ├── system-overview.md       # High-level architecture
│   ├── api-specification.md     # API documentation
│   ├── database-schema.md       # Data models
│   └── deployment-guide.md      # Infrastructure setup
├── development/                 # Developer guides
│   ├── getting-started.md       # Local development setup
│   ├── coding-standards.md      # Code style guidelines
│   ├── testing-guidelines.md    # Testing strategies
│   └── contributing.md          # Contribution process
└── user-guides/                 # End-user documentation
    ├── installation.md          # Installation instructions
    ├── user-manual.md           # Feature documentation
    └── troubleshooting.md       # Common issues and solutions
```

## 🧪 **Testing Structure**

```
tests/
├── unit/                        # Unit tests
│   ├── frontend/                # React component tests
│   └── backend/                 # Python service tests
├── integration/                 # Service integration tests
│   ├── api/                     # API endpoint tests
│   └── database/                # Database integration tests
├── e2e/                         # End-to-end tests
│   ├── playwright/              # Browser automation tests
│   └── scenarios/               # User workflow tests
└── performance/                 # Load and performance tests
    ├── load-tests/              # Load testing scripts
    └── benchmarks/              # Performance benchmarks
```

## 🔧 **Configuration Structure**

```
config/
├── development/                 # Local development configs
│   ├── docker-compose.yml       # Dev services
│   ├── api-config.yml           # API configuration
│   └── database-config.yml      # Database settings
├── staging/                     # Staging environment
├── production/                  # Production environment
└── local/                       # Local overrides (gitignored)
    ├── .env                     # Environment variables
    └── local-config.yml         # Local configuration overrides
```

## 🏗️ **Architecture Patterns**

### **Service Communication**
- **Synchronous**: REST APIs for request-response patterns
- **Asynchronous**: Redis Streams for real-time data flow
- **Event-Driven**: Domain events for service decoupling

### **Data Flow**
```
TEP Simulator → Redis Stream → Anomaly Detection → WebSocket → Frontend
                     ↓
              Historical Storage (TDengine)
                     ↓
              LLM Analysis (on anomaly) → Knowledge Base
```

### **Error Handling**
- **Frontend**: Error boundaries with user-friendly messages
- **Backend**: Structured error responses with correlation IDs
- **Monitoring**: Centralized error tracking with Sentry integration

### **Security Layers**
- **Network**: VPN access, firewall rules
- **Application**: JWT authentication, RBAC authorization
- **Data**: Encryption at rest and in transit
- **Audit**: Comprehensive logging of all user actions

This structure ensures clear separation of concerns, maintainable code organization, and scalable architecture patterns suitable for industrial applications.
