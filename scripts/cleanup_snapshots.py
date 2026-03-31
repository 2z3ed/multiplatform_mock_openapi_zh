#!/usr/bin/env python3
"""
Snapshot Cleanup Script

Cleanup old snapshots based on retention days.
Default mode is dry-run (preview only).
Use --execute to perform actual deletion.

Usage:
    python scripts/cleanup_snapshots.py --help
    python scripts/cleanup_snapshots.py --retention-days 7
    python scripts/cleanup_snapshots.py --retention-days 7 --execute
    python scripts/cleanup_snapshots.py --type inventory --retention-days 7
    python scripts/cleanup_snapshots.py --type all --execute
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'domain-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'domain-models'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from shared_db import get_db_url
from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository


def get_db_session():
    """Get database session using existing configuration."""
    db_url = get_db_url()
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def cleanup_inventory(session, retention_days: int, dry_run: bool) -> dict:
    """Cleanup inventory snapshots."""
    repo = ERPInventorySnapshotRepository(session)
    return repo.cleanup_old_snapshots(retention_days=retention_days, dry_run=dry_run)


def cleanup_audit(session, retention_days: int, dry_run: bool) -> dict:
    """Cleanup order audit snapshots."""
    repo = OrderAuditSnapshotRepository(session)
    return repo.cleanup_old_snapshots(retention_days=retention_days, dry_run=dry_run)


def cleanup_exception(session, retention_days: int, dry_run: bool) -> dict:
    """Cleanup order exception snapshots."""
    repo = OrderExceptionSnapshotRepository(session)
    return repo.cleanup_old_snapshots(retention_days=retention_days, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup old snapshots based on retention days.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Preview cleanup with default 7 days retention
  %(prog)s --retention-days 14          Preview cleanup with 14 days retention
  %(prog)s --execute                    Execute cleanup with default settings
  %(prog)s --type inventory --execute   Execute cleanup for inventory only
        """
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute actual deletion (default is dry-run/preview only)",
    )
    
    parser.add_argument(
        "--retention-days",
        type=int,
        default=7,
        help="Number of days to retain snapshots (default: 7)",
    )
    
    parser.add_argument(
        "--type",
        choices=["inventory", "order_audit", "order_exception", "all"],
        default="all",
        help="Type of snapshots to cleanup (default: all)",
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    retention_days = args.retention_days
    cleanup_type = args.type
    
    print("=" * 50)
    print("Snapshot Cleanup")
    print("=" * 50)
    print(f"Retention days: {retention_days}")
    print(f"Type: {cleanup_type}")
    print(f"Mode: {'dry-run' if dry_run else 'execute'}")
    print()
    
    session = get_db_session()
    
    try:
        results = {}
        
        if cleanup_type in ["inventory", "all"]:
            results["inventory"] = cleanup_inventory(session, retention_days, dry_run)
        
        if cleanup_type in ["order_audit", "all"]:
            results["order_audit"] = cleanup_audit(session, retention_days, dry_run)
        
        if cleanup_type in ["order_exception", "all"]:
            results["order_exception"] = cleanup_exception(session, retention_days, dry_run)
        
        total_to_delete = 0
        total_deleted = 0
        
        for snapshot_type, result in results.items():
            print(f"{snapshot_type} snapshots:")
            print(f"  Total: {result['total_count']}")
            print(f"  To delete: {result['to_delete_count']}")
            print(f"  Protected: {result['protected_count']}")
            if not dry_run:
                print(f"  Deleted: {result['deleted_count']}")
            print()
            
            total_to_delete += result['to_delete_count']
            total_deleted += result['deleted_count']
        
        print("-" * 50)
        print(f"Summary: {total_to_delete} records to delete")
        
        if dry_run:
            print("Run with --execute to perform deletion.")
        else:
            print(f"Deleted: {total_deleted} records")
        
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
