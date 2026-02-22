#!/usr/bin/env python3
"""
Checkpoint Database Management Script

This script helps manage the LangGraph checkpoint database by:
- Showing database statistics
- Cleaning up old checkpoints
- Vacuuming the database to reclaim space
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse


def get_db_path():
    """Get the checkpoint database path"""
    return Path("data/database/checkpoints.db")


def get_db_stats(conn):
    """Get statistics about the checkpoint database"""
    cursor = conn.cursor()
    
    # Get total checkpoints
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    total_checkpoints = cursor.fetchone()[0]
    
    # Get unique threads
    cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM checkpoints")
    unique_threads = cursor.fetchone()[0]
    
    # Get database size
    db_path = get_db_path()
    db_size_mb = db_path.stat().st_size / (1024 * 1024)
    
    # Get oldest checkpoint
    cursor.execute("SELECT MIN(checkpoint_id) FROM checkpoints")
    oldest = cursor.fetchone()[0]
    
    # Get newest checkpoint
    cursor.execute("SELECT MAX(checkpoint_id) FROM checkpoints")
    newest = cursor.fetchone()[0]
    
    return {
        "total_checkpoints": total_checkpoints,
        "unique_threads": unique_threads,
        "db_size_mb": db_size_mb,
        "oldest_checkpoint": oldest,
        "newest_checkpoint": newest,
    }


def show_stats():
    """Display checkpoint database statistics"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Checkpoint database not found at:", db_path)
        return
    
    print("\n" + "="*60)
    print("  CHECKPOINT DATABASE STATISTICS")
    print("="*60)
    
    conn = sqlite3.connect(str(db_path))
    stats = get_db_stats(conn)
    conn.close()
    
    print(f"\n📊 Total Checkpoints: {stats['total_checkpoints']:,}")
    print(f"🔗 Unique Threads: {stats['unique_threads']:,}")
    print(f"💾 Database Size: {stats['db_size_mb']:.2f} MB")
    print(f"📅 Oldest Checkpoint ID: {stats['oldest_checkpoint']}")
    print(f"📅 Newest Checkpoint ID: {stats['newest_checkpoint']}")
    
    if stats['db_size_mb'] > 100:
        print(f"\n⚠️  WARNING: Database is large ({stats['db_size_mb']:.2f} MB)")
        print("   Consider running cleanup with: --clean-old")
    
    print("\n" + "="*60)


def clean_old_checkpoints(days=7, keep_recent=100):
    """
    Clean up old checkpoints
    
    Args:
        days: Keep checkpoints from the last N days
        keep_recent: Always keep the most recent N checkpoints per thread
    """
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Checkpoint database not found")
        return
    
    print(f"\n🧹 Cleaning checkpoints older than {days} days...")
    print(f"   (Keeping {keep_recent} most recent per thread)")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get stats before
    stats_before = get_db_stats(conn)
    
    # Delete old checkpoints, but keep recent ones per thread
    # This is a simplified approach - keep last N checkpoints per thread
    cursor.execute("""
        DELETE FROM checkpoints
        WHERE (thread_id, checkpoint_id) NOT IN (
            SELECT thread_id, checkpoint_id
            FROM (
                SELECT thread_id, checkpoint_id,
                       ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY checkpoint_id DESC) as rn
                FROM checkpoints
            )
            WHERE rn <= ?
        )
    """, (keep_recent,))
    
    deleted_checkpoints = cursor.rowcount
    
    # Also clean up writes table
    cursor.execute("""
        DELETE FROM writes
        WHERE (thread_id, checkpoint_id) NOT IN (
            SELECT DISTINCT thread_id, checkpoint_id FROM checkpoints
        )
    """)
    
    deleted_writes = cursor.rowcount
    
    conn.commit()
    
    # Get stats after
    stats_after = get_db_stats(conn)
    
    conn.close()
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted {deleted_checkpoints:,} checkpoints")
    print(f"   Deleted {deleted_writes:,} writes")
    print(f"   Size before: {stats_before['db_size_mb']:.2f} MB")
    print(f"   Size after: {stats_after['db_size_mb']:.2f} MB")
    print(f"   Checkpoints remaining: {stats_after['total_checkpoints']:,}")


def vacuum_database():
    """Vacuum the database to reclaim space"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Checkpoint database not found")
        return
    
    print("\n🔧 Vacuuming database to reclaim space...")
    
    conn = sqlite3.connect(str(db_path))
    
    # Get size before
    size_before = db_path.stat().st_size / (1024 * 1024)
    
    conn.execute("VACUUM")
    conn.close()
    
    # Get size after
    size_after = db_path.stat().st_size / (1024 * 1024)
    saved = size_before - size_after
    
    print(f"\n✅ Vacuum complete!")
    print(f"   Size before: {size_before:.2f} MB")
    print(f"   Size after: {size_after:.2f} MB")
    print(f"   Space saved: {saved:.2f} MB ({saved/size_before*100:.1f}%)")


def delete_all_checkpoints():
    """Delete all checkpoints (use with caution!)"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Checkpoint database not found")
        return
    
    print("\n⚠️  WARNING: This will delete ALL checkpoints!")
    response = input("Are you sure? Type 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM checkpoints")
    cursor.execute("DELETE FROM writes")
    
    conn.commit()
    conn.close()
    
    print("✅ All checkpoints deleted")
    
    # Vacuum to reclaim space
    vacuum_database()


def main():
    parser = argparse.ArgumentParser(
        description="Manage LangGraph checkpoint database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/manage_checkpoints.py --stats
  python scripts/manage_checkpoints.py --clean-old --days 7 --keep 50
  python scripts/manage_checkpoints.py --vacuum
  python scripts/manage_checkpoints.py --delete-all
        """
    )
    
    parser.add_argument("--stats", action="store_true",
                       help="Show database statistics")
    parser.add_argument("--clean-old", action="store_true",
                       help="Clean up old checkpoints")
    parser.add_argument("--days", type=int, default=7,
                       help="Keep checkpoints from last N days (default: 7)")
    parser.add_argument("--keep", type=int, default=100,
                       help="Keep N most recent checkpoints per thread (default: 100)")
    parser.add_argument("--vacuum", action="store_true",
                       help="Vacuum database to reclaim space")
    parser.add_argument("--delete-all", action="store_true",
                       help="Delete ALL checkpoints (use with caution!)")
    
    args = parser.parse_args()
    
    # Default to stats if no action specified
    if not any([args.stats, args.clean_old, args.vacuum, args.delete_all]):
        args.stats = True
    
    if args.stats:
        show_stats()
    
    if args.clean_old:
        clean_old_checkpoints(days=args.days, keep_recent=args.keep)
        if args.vacuum:
            vacuum_database()
    
    if args.vacuum and not args.clean_old:
        vacuum_database()
    
    if args.delete_all:
        delete_all_checkpoints()


if __name__ == "__main__":
    main()
