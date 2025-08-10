# TEP Industrial Intelligence Platform - Development Commands

.PHONY: help dev-up dev-down dev-logs dev-shell test-all lint format clean

# Default target
help:
	@echo "🏭 TEP Industrial Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  dev-up          Start all development services"
	@echo "  dev-down        Stop all development services"
	@echo "  dev-logs        View service logs"
	@echo "  dev-shell       Access service shell"
	@echo "  dev-reset       Reset development environment"
	@echo ""
	@echo "  test-unit       Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-e2e        Run end-to-end tests"
	@echo "  test-all        Run all tests"
	@echo ""
	@echo "  lint            Run code linters"
	@echo "  format          Format code"
	@echo "  type-check      Run type checking"
	@echo ""
	@echo "  db-migrate      Run database migrations"
	@echo "  db-seed         Seed test data"
	@echo "  db-reset        Reset database"
	@echo ""
	@echo "  clean           Clean up containers and volumes"
	@echo "  prod-build      Build production images"
	@echo "  prod-deploy     Deploy to production"

# Development Environment
dev-up:
	@echo "🚀 Starting TEP Industrial Intelligence Platform..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 API Gateway: http://localhost:8000"
	@echo "📊 Grafana: http://localhost:3001 (admin/admin)"
	@echo "🗄️ pgAdmin: http://localhost:8080 (admin@tep.local/admin)"

dev-down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

dev-logs:
	docker-compose logs -f

dev-shell:
	@echo "Select service:"
	@echo "1) api-gateway"
	@echo "2) simulation"
	@echo "3) llm-analysis"
	@echo "4) anomaly-detection"
	@echo "5) frontend"
	@read -p "Enter choice [1-5]: " choice; \
	case $$choice in \
		1) docker-compose exec api-gateway /bin/bash ;; \
		2) docker-compose exec simulation /bin/bash ;; \
		3) docker-compose exec llm-analysis /bin/bash ;; \
		4) docker-compose exec anomaly-detection /bin/bash ;; \
		5) docker-compose exec frontend /bin/bash ;; \
		*) echo "Invalid choice" ;; \
	esac

dev-reset:
	@echo "🔄 Resetting development environment..."
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Environment reset complete!"

# Monitoring & Tools
monitoring-up:
	@echo "📊 Starting monitoring stack..."
	docker-compose --profile monitoring up -d
	@echo "✅ Monitoring started!"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📈 Grafana: http://localhost:3001"

tools-up:
	@echo "🔧 Starting development tools..."
	docker-compose --profile tools up -d
	@echo "✅ Tools started!"
	@echo "🗄️ pgAdmin: http://localhost:8080"
	@echo "📝 Redis Commander: http://localhost:8081"

# Testing
test-unit:
	@echo "🧪 Running unit tests..."
	docker-compose exec frontend npm test -- --coverage --watchAll=false
	docker-compose exec api-gateway pytest tests/unit/ -v --cov=app

test-integration:
	@echo "🔗 Running integration tests..."
	docker-compose exec api-gateway pytest tests/integration/ -v

test-e2e:
	@echo "🌐 Running end-to-end tests..."
	docker-compose exec frontend npx playwright test

test-all: test-unit test-integration test-e2e
	@echo "✅ All tests completed!"

# Code Quality
lint:
	@echo "🔍 Running linters..."
	docker-compose exec frontend npm run lint
	docker-compose exec api-gateway flake8 app/
	docker-compose exec api-gateway black --check app/
	docker-compose exec api-gateway isort --check-only app/

format:
	@echo "✨ Formatting code..."
	docker-compose exec frontend npm run format
	docker-compose exec api-gateway black app/
	docker-compose exec api-gateway isort app/

type-check:
	@echo "🔍 Running type checks..."
	docker-compose exec frontend npm run type-check
	docker-compose exec api-gateway mypy app/

# Database Management
db-migrate:
	@echo "🗄️ Running database migrations..."
	docker-compose exec api-gateway alembic upgrade head

db-seed:
	@echo "🌱 Seeding test data..."
	docker-compose exec api-gateway python scripts/seed_data.py

db-reset:
	@echo "🔄 Resetting database..."
	docker-compose exec postgres psql -U tep_user -d tep_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-migrate
	$(MAKE) db-seed

# Production
prod-build:
	@echo "🏗️ Building production images..."
	docker-compose -f docker-compose.prod.yml build

prod-deploy:
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup complete!"

# Health Checks
health:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health | jq '.' || echo "❌ API Gateway unhealthy"
	@curl -s http://localhost:8001/health | jq '.' || echo "❌ Simulation Service unhealthy"
	@curl -s http://localhost:8002/health | jq '.' || echo "❌ LLM Service unhealthy"
	@curl -s http://localhost:8003/health | jq '.' || echo "❌ Anomaly Service unhealthy"

# Development Utilities
install-deps:
	@echo "📦 Installing dependencies..."
	cd src/frontend && npm install
	cd src/backend/api-gateway && pip install -r requirements.txt
	cd src/backend/services/simulation && pip install -r requirements.txt
	cd src/backend/services/llm-analysis && pip install -r requirements.txt
	cd src/backend/services/anomaly-detection && pip install -r requirements.txt

generate-docs:
	@echo "📚 Generating API documentation..."
	docker-compose exec api-gateway python scripts/generate_openapi.py

backup-data:
	@echo "💾 Backing up data..."
	docker-compose exec postgres pg_dump -U tep_user tep_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backup created!"

# Quick Start
quick-start: dev-up
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	$(MAKE) health
	@echo ""
	@echo "🎉 TEP Industrial Intelligence Platform is ready!"
	@echo "🌐 Open http://localhost:3000 to get started"
