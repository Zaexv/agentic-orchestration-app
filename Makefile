.PHONY: help install run-local test clean lint format

help: ## Show this help message
	@echo "Digital Twin AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies in virtual environment
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

run-local: ## Run the FastAPI server locally
	. venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the FastAPI server in production mode (no reload)
	. venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run all tests
	. venv/bin/activate && pytest tests/ -v

test-state: ## Run state management tests only
	. venv/bin/activate && pytest tests/test_state.py -v

test-agents: ## Run agent tests only
	. venv/bin/activate && pytest tests/test_agents.py -v

test-routing: ## Run routing logic tests only
	. venv/bin/activate && pytest tests/test_routing.py -v

test-api: ## Run API endpoint tests only
	. venv/bin/activate && pytest tests/test_api.py -v

test-all: ## Run all tests with summary
	. venv/bin/activate && pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	. venv/bin/activate && pytest tests/ --cov=app --cov-report=html --cov-report=term

lint: ## Run linter (ruff)
	. venv/bin/activate && ruff check app/ tests/

format: ## Format code with black
	. venv/bin/activate && black app/ tests/

format-check: ## Check code formatting without making changes
	. venv/bin/activate && black --check app/ tests/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

clean-all: clean ## Clean up everything including virtual environment
	rm -rf venv/

setup: install ## Complete setup: create venv and install dependencies
	@echo "✅ Setup complete! Run 'make run-local' to start the server."

check-api: ## Quick API health check
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/health || echo "❌ Server not running. Run 'make run-local' first."

docs: ## Open API documentation in browser
	@echo "Opening API docs at http://localhost:8000/docs"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs 2>/dev/null || echo "Visit http://localhost:8000/docs manually"
