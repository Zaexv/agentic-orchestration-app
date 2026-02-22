# Managing Checkpoint Database Size

## Problem

The LangGraph checkpoint database (`data/database/checkpoints.db`) can grow very large over time:
- Each conversation turn creates checkpoints
- Checkpoints store full state (messages, routing history, etc.)
- Database can easily reach several GB with testing

**This database should NOT be committed to GitHub!**

## Solution

### 1. Added to `.gitignore`

The checkpoint database is now excluded from git:

```gitignore
# In .gitignore
data/database/checkpoints.db
data/database/checkpoints.db-shm
data/database/checkpoints.db-wal
```

**Verify it's ignored:**
```bash
git status data/database/checkpoints.db
# Should show: "Ignored files"
```

### 2. Management Script

Use `scripts/manage_checkpoints.py` to manage the database:

**Show Statistics:**
```bash
uv run python scripts/manage_checkpoints.py --stats
```

**Clean Old Checkpoints:**
```bash
# Keep only 50 most recent checkpoints per conversation thread
uv run python scripts/manage_checkpoints.py --clean-old --keep 50 --vacuum
```

**Delete Everything (careful!):**
```bash
uv run python scripts/manage_checkpoints.py --delete-all
```

## Best Practices

### Development

**Regular Cleanup:**
```bash
# Weekly cleanup - keep last 20 checkpoints per thread
uv run python scripts/manage_checkpoints.py --clean-old --keep 20 --vacuum
```

**Before Committing:**
```bash
# Check database isn't being tracked
git status | grep checkpoints
# Should be empty or show "Ignored"
```

### Production

**1. Use PostgreSQL Checkpointer**

For production, migrate to PostgreSQL:

```python
# In app/orchestration/graph.py
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

# Connect to PostgreSQL
conn = psycopg.connect("postgresql://user:pass@host/db")
checkpointer = PostgresSaver(conn)
```

**Benefits:**
- Better performance at scale
- Built-in cleanup and maintenance
- Concurrent access support
- Can use managed database services

**2. Implement Automatic Cleanup**

Add a scheduled task to clean old checkpoints:

```python
# Example: Clean checkpoints older than 7 days, keep 100 recent per thread
from apscheduler.schedulers.background import BackgroundScheduler

def cleanup_checkpoints():
    # Run cleanup script
    import subprocess
    subprocess.run([
        "python", "scripts/manage_checkpoints.py",
        "--clean-old", "--keep", "100", "--vacuum"
    ])

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_checkpoints, 'cron', hour=2)  # 2 AM daily
scheduler.start()
```

**3. Monitor Database Size**

```bash
# Add to monitoring/alerting
watch -n 300 'du -h data/database/checkpoints.db'
```

### Docker Deployment

**In `docker-compose.yml`, use a volume:**

```yaml
services:
  backend:
    volumes:
      - checkpoint-data:/app/data/database

volumes:
  checkpoint-data:
    # This persists data but isn't in git
```

**Or use PostgreSQL service:**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: checkpoints
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

## Checkpoint Retention Policy

### Recommended Settings

| Environment | Keep Recent | Cleanup Frequency |
|-------------|-------------|-------------------|
| Development | 10-20 per thread | Weekly |
| Staging | 50-100 per thread | Daily |
| Production | 100-500 per thread | Hourly |

### Sizing Estimates

- **Per checkpoint:** ~50-500KB (depends on conversation length)
- **100 checkpoints:** ~5-50MB
- **1000 checkpoints:** ~50-500MB
- **10,000 checkpoints:** ~500MB-5GB

## Configuration

Add to `.env`:

```bash
# Checkpoint retention settings
CHECKPOINT_CLEANUP_ENABLED=true
CHECKPOINT_KEEP_RECENT=100
CHECKPOINT_CLEANUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
```

Then implement in your app:

```python
# app/config/settings.py
class Settings(BaseSettings):
    checkpoint_cleanup_enabled: bool = False
    checkpoint_keep_recent: int = 100
    checkpoint_cleanup_schedule: str = "0 2 * * *"
```

## Troubleshooting

### Database too large, git complaining

```bash
# If you accidentally committed it:
git rm --cached data/database/checkpoints.db
git commit -m "Remove checkpoint database from git"

# Add to .gitignore
echo "data/database/checkpoints.db" >> .gitignore
git add .gitignore
git commit -m "Ignore checkpoint database"
```

### Vacuum taking too long

```bash
# Option 1: Delete and recreate
rm data/database/checkpoints.db
# Database will be recreated on next run

# Option 2: Vacuum in background
nohup uv run python scripts/manage_checkpoints.py --vacuum &
```

### Out of disk space

```bash
# Emergency cleanup - keep only 5 most recent
uv run python scripts/manage_checkpoints.py --clean-old --keep 5 --vacuum

# Or delete all
uv run python scripts/manage_checkpoints.py --delete-all
```

### Checkpoint database corruption

```bash
# Check integrity
sqlite3 data/database/checkpoints.db "PRAGMA integrity_check;"

# If corrupted, backup and recreate
mv data/database/checkpoints.db data/database/checkpoints.db.backup
# Database will be recreated on next run
```

## Alternative: Disable Checkpointing

If you don't need conversation memory across restarts:

```python
# app/orchestration/graph.py

# Comment out checkpointer
# checkpointer = SqliteSaver(_checkpoint_conn)

# Compile without checkpointer
workflow_app = create_workflow(checkpointer=None)
```

**Note:** This disables conversation memory across requests!

## Summary

✅ **Added to .gitignore** - Won't be committed
✅ **Management script** - Easy cleanup
✅ **Documentation** - Best practices
✅ **Production path** - PostgreSQL migration

**Recommended Action:**
```bash
# Clean up now
uv run python scripts/manage_checkpoints.py --clean-old --keep 10 --vacuum

# Add to weekly maintenance
# (Add to crontab or create a scheduled task)
```

## Files

- `.gitignore` - Updated with checkpoint exclusions
- `scripts/manage_checkpoints.py` - Database management tool
- This document - Management guide
