.PHONY: help install sync run-local test clean lint format

help: ## Show this help message
	@echo "Digital Twin AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: sync ## Alias for sync (backwards compatibility)

sync: ## Sync dependencies with UV
	uv sync

sync-prod: ## Sync production dependencies only (no dev)
	uv sync --no-dev

run-local: ## Run the FastAPI server locally
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the FastAPI server in production mode (no reload)
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Run all tests
	uv run pytest tests/ -v

test-state: ## Run state management tests only
	uv run pytest tests/test_state.py -v

test-agents: ## Run agent tests only
	uv run pytest tests/test_agents.py -v

test-routing: ## Run routing logic tests only
	uv run pytest tests/test_routing.py -v

test-router: ## Run router tests only
	uv run pytest tests/test_router.py -v

test-api: ## Run API endpoint tests only
	uv run pytest tests/test_api.py -v

test-all: ## Run all tests with summary
	uv run pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	uv run pytest tests/ --cov=app --cov-report=html --cov-report=term

lint: ## Run linter (ruff)
	uv run ruff check app/ tests/

lint-fix: ## Run linter and fix issues
	uv run ruff check --fix app/ tests/

format: ## Format code with black
	uv run black app/ tests/
	uv run isort app/ tests/

format-check: ## Check code formatting without making changes
	uv run black --check app/ tests/
	uv run isort --check-only app/ tests/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

clean-all: clean ## Clean up everything including virtual environment
	rm -rf .venv/ venv/

setup: sync ## Complete setup: sync dependencies with UV
	@echo "✅ Setup complete! Run 'make run-local' to start the server."

check-api: ## Quick API health check
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/health || echo "❌ Server not running. Run 'make run-local' first."

docs: ## Open API documentation in browser
	@echo "Opening API docs at http://localhost:8000/docs"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs 2>/dev/null || echo "Visit http://localhost:8000/docs manually"

# UV specific commands
uv-lock: ## Update uv.lock file
	uv lock

uv-update: ## Update all dependencies to latest versions
	uv lock --upgrade

uv-add: ## Add a new dependency (usage: make uv-add PKG=package-name)
	uv add $(PKG)

uv-add-dev: ## Add a new dev dependency (usage: make uv-add-dev PKG=package-name)
	uv add --dev $(PKG)
