# Checkpoint Database Management - Quick Reference

## ✅ What Was Done

1. **Added to `.gitignore`:**
   - `data/database/checkpoints.db`
   - `data/database/checkpoints.db-shm`
   - `data/database/checkpoints.db-wal`

2. **Removed from git tracking:**
   - Checkpoint files will no longer be committed
   - Previous commit removed them from repository

3. **Created management script:**
   - `scripts/manage_checkpoints.py`
   - Clean, vacuum, and monitor checkpoint database

4. **Cleaned up database:**
   - Before: 13.2 GB
   - After: 5.1 GB
   - **Saved: 8GB (60%)**

## 🚀 Quick Commands

```bash
# Show database stats
uv run python scripts/manage_checkpoints.py --stats

# Weekly cleanup (recommended)
uv run python scripts/manage_checkpoints.py --clean-old --keep 20 --vacuum

# Emergency cleanup (keeps only 5 recent per thread)
uv run python scripts/manage_checkpoints.py --clean-old --keep 5 --vacuum

# Delete everything
uv run python scripts/manage_checkpoints.py --delete-all
```

## 📋 Recommended Maintenance

### Development
```bash
# Run weekly
uv run python scripts/manage_checkpoints.py --clean-old --keep 20 --vacuum
```

### Before Committing Code
```bash
# Verify checkpoint DB is ignored
git status | grep checkpoint
# Should show nothing or "Ignored"
```

### If Database Gets Too Large
```bash
# 1. Check size
ls -lh data/database/checkpoints.db

# 2. Clean aggressively
uv run python scripts/manage_checkpoints.py --clean-old --keep 5 --vacuum

# 3. Or delete and recreate
rm data/database/checkpoints.db
# Will be recreated on next app start
```

## 🎯 Next Steps

### Option 1: Keep SQLite (Simple)
- ✅ Current setup works fine for development
- ⚠️ Remember to run cleanup weekly
- ⚠️ Database won't be in git (each dev has own)

### Option 2: Migrate to PostgreSQL (Production)
```python
# In app/orchestration/graph.py
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

conn = psycopg.connect(DATABASE_URL)
checkpointer = PostgresSaver(conn)
```

Benefits:
- Better performance at scale
- Automatic maintenance
- Shared across team
- Production-ready

### Option 3: Disable Checkpointing (Simple Apps)
```python
# In app/orchestration/graph.py
workflow_app = create_workflow(checkpointer=None)
```

Removes conversation memory but simplifies deployment.

## 📁 Files

- `.gitignore` - Updated with checkpoint exclusions
- `scripts/manage_checkpoints.py` - Management tool
- `docs/CHECKPOINT_DATABASE_MANAGEMENT.md` - Full guide

## ⚠️ Important

- **Never commit checkpoint database to git**
- **Run cleanup regularly** to prevent disk space issues
- **Each developer will have their own checkpoint database**
- **Conversations won't be shared between team members**

## 💡 Pro Tips

1. **Add to Makefile:**
```makefile
cleanup-checkpoints:
    uv run python scripts/manage_checkpoints.py --clean-old --keep 20 --vacuum
```

2. **Add to CI/CD:**
```yaml
# .github/workflows/test.yml
- name: Setup test database
  run: |
    mkdir -p data/database
    # Checkpoint DB created automatically
```

3. **Monitor in development:**
```bash
# Add to .bashrc or .zshrc
alias checkpoint-stats='uv run python scripts/manage_checkpoints.py --stats'
```

---

**Status:** ✅ Checkpoint database is now properly managed and excluded from git!
