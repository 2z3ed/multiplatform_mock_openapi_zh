"""
Integration Scheduler for controlled scheduled refresh.
Only starts when ODOO_PROVIDER_MODE=real and ODOO_SCHEDULED_REFRESH_ENABLED=true.
"""

import os
import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None
_started: bool = False


def _get_config() -> tuple[bool, str, int, int]:
    """Get scheduler configuration from environment."""
    provider_mode = os.getenv("ODOO_PROVIDER_MODE", "mock").lower()
    enabled = os.getenv("ODOO_SCHEDULED_REFRESH_ENABLED", "false").lower() == "true"
    inventory_interval = int(os.getenv("ODOO_REFRESH_INTERVAL_INVENTORY", "900"))
    audit_interval = int(os.getenv("ODOO_REFRESH_INTERVAL_AUDIT", "1800"))
    return enabled, provider_mode, inventory_interval, audit_interval


def _create_scheduler() -> BackgroundScheduler:
    """Create a new scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def _refresh_inventory_job():
    """Job function for inventory refresh."""
    from shared_db import SessionLocal
    from app.services.integration_service import IntegrationService
    from providers.odoo.provider_factory import get_odoo_provider
    
    logger.info("[SCHEDULER] Starting scheduled inventory refresh")
    
    db_session = SessionLocal()
    try:
        provider = get_odoo_provider()
        service = IntegrationService(db_session, odoo_provider=provider)
        result = service.refresh_inventory(trigger_type="scheduled")
        logger.info(f"[SCHEDULER] Inventory refresh completed: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Inventory refresh failed: {e}")
    finally:
        db_session.close()


def _refresh_audit_job():
    """Job function for audit refresh."""
    from shared_db import SessionLocal
    from app.services.integration_service import IntegrationService
    from providers.odoo.provider_factory import get_odoo_provider
    
    logger.info("[SCHEDULER] Starting scheduled audit refresh")
    
    db_session = SessionLocal()
    try:
        provider = get_odoo_provider()
        service = IntegrationService(db_session, odoo_provider=provider)
        result = service.refresh_audit(trigger_type="scheduled")
        logger.info(f"[SCHEDULER] Audit refresh completed: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Audit refresh failed: {e}")
    finally:
        db_session.close()


def start_scheduler() -> bool:
    """
    Start the scheduler if conditions are met.
    
    Returns:
        True if scheduler started, False otherwise.
    """
    global _started
    
    if _started:
        logger.info("[SCHEDULER] Already started, skipping")
        return True
    
    enabled, provider_mode, inventory_interval, audit_interval = _get_config()
    
    if not enabled:
        logger.info("[SCHEDULER] Disabled by configuration (ODOO_SCHEDULED_REFRESH_ENABLED=false)")
        return False
    
    if provider_mode != "real":
        logger.info(f"[SCHEDULER] Not starting in '{provider_mode}' mode, only 'real' mode supported")
        return False
    
    scheduler = _create_scheduler()
    
    scheduler.add_job(
        _refresh_inventory_job,
        trigger=IntervalTrigger(seconds=inventory_interval),
        id="refresh_inventory",
        name="Inventory Refresh",
        replace_existing=True,
    )
    
    scheduler.add_job(
        _refresh_audit_job,
        trigger=IntervalTrigger(seconds=audit_interval),
        id="refresh_audit",
        name="Audit Refresh",
        replace_existing=True,
    )
    
    scheduler.start()
    _started = True
    
    logger.info(
        f"[SCHEDULER] Started with inventory_interval={inventory_interval}s, "
        f"audit_interval={audit_interval}s"
    )
    
    return True


def stop_scheduler():
    """Stop the scheduler if running."""
    global _started, _scheduler
    
    if _scheduler is not None and _started:
        _scheduler.shutdown(wait=False)
        _started = False
        logger.info("[SCHEDULER] Stopped")


def is_scheduler_running() -> bool:
    """Check if the scheduler is running."""
    return _started
