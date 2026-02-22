# CI Pipeline Documentation

## Overview

A simple CI pipeline to test that both frontend and backend compile and pass core tests.

## Files Created

1. **`.github/workflows/ci.yml`** - GitHub Actions workflow
2. **`Makefile`** - Added `ci`, `ci-backend`, and `ci-frontend` targets

## What It Tests

### Backend
- ✅ Core state management tests (test_state.py)
- ✅ Routing logic tests (test_routing.py)
- ✅ Backend imports correctly

### Frontend
- ✅ ESLint passes (code quality)
- ✅ Build succeeds (Vite compilation)
- ✅ Dist folder is created

## Running Locally

```bash
# Full CI pipeline (backend + frontend)
make ci

# Backend only
make ci-backend

# Frontend only
make ci-frontend
```

## GitHub Actions

The pipeline runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### Jobs

1. **Backend** - Python 3.12, UV package manager, pytest
2. **Frontend** - Node.js 20, npm, ESLint + Vite build

Both jobs run in parallel for fast feedback.

## Test Results

Current status: **38 tests passing** ✅

```bash
tests/test_state.py ............ (13 passed)
tests/test_routing.py .......... (25 passed)
```

## What's NOT Tested

To keep CI fast and simple, these are excluded:
- Integration tests (test_api.py)
- Agent tests (test_agents.py) - some legacy issues
- Checkpointing tests - require full app imports

These can be run manually with:
```bash
make test-all  # Run ALL tests
```

## CI Pipeline Output

Successful run looks like:
```
🚀 Running CI Pipeline...

📦 Backend Tests (core functionality)...
tests/test_state.py::test_create_initial_state PASSED
tests/test_state.py::test_add_message PASSED
... (38 passed in 1.90s)

✅ Backend imports...
✅ Backend imports OK

🎨 Frontend Lint...
⠙ (passes silently)

🏗️  Frontend Build...
dist/index.html                   0.46 kB │ gzip: 0.30 kB
dist/assets/index-xxx.css        42.72 kB │ gzip: 10.98 kB
dist/assets/index-xxx.js       2161.72 kB │ gzip: 658.12 kB
✓ built in 4.10s

✅ CI Pipeline Complete!
```

## Fixing Issues

### Backend Fails
```bash
# Run specific test file
pytest tests/test_state.py -v

# Check imports
python -c "from app.main import app; print('OK')"
```

### Frontend Fails
```bash
cd front_end

# Check lint errors
npm run lint

# Try building
npm run build
```

## Configuration

### Backend Tests
Located in `Makefile` line ~96:
```makefile
@uv run pytest tests/test_state.py tests/test_routing.py -v --tb=short
```

To add more tests, append to the pytest command.

### Frontend Build
Node version: 20 (configured in `.github/workflows/ci.yml`)
Package manager: npm (using `package-lock.json`)

## Notes

- CI is intentionally "stupid" - it just checks compilation + core tests
- Fast feedback (~2 minutes total)
- Catches most breaking changes
- Full test suite can be run separately with `make test-all`

## Troubleshooting

**Issue**: Tests fail with "ModuleNotFoundError"
- **Fix**: Run `uv sync` to install dependencies

**Issue**: Frontend build fails
- **Fix**: Run `cd front_end && npm install`

**Issue**: ESLint errors
- **Fix**: Run `cd front_end && npm run lint` to see errors
- Auto-fix: `cd front_end && npx eslint . --fix`

**Issue**: GitHub Actions fails but local passes
- Check Python/Node versions match
- Ensure all dependencies in `pyproject.toml` and `package.json`
- Check `.gitignore` isn't excluding needed files
