"""
Provider Factory for Odoo integration.
Provides controlled provider selection based on configuration.
"""

import os
from typing import Optional


class ProviderConfigError(Exception):
    """Raised when provider configuration is invalid."""
    pass


def get_odoo_provider():
    """
    Get Odoo provider based on ODOO_PROVIDER_MODE configuration.
    
    Priority:
    1. Explicit injection (handled by caller)
    2. Configuration (this function)
    
    Returns:
        OdooMockProvider or OdooRealProvider based on configuration.
        
    Raises:
        ProviderConfigError: If ODOO_PROVIDER_MODE=real but required config is missing.
    """
    from providers.odoo.mock.provider import OdooMockProvider
    from providers.odoo.real.client import OdooClient
    from providers.odoo.real.provider import OdooRealProvider
    
    provider_mode = os.getenv("ODOO_PROVIDER_MODE", "mock").lower()
    
    if provider_mode == "mock":
        return OdooMockProvider()
    
    if provider_mode == "real":
        required_vars = [
            "ODOO_BASE_URL",
            "ODOO_DB",
            "ODOO_USERNAME",
            "ODOO_API_KEY",
        ]
        missing = [v for v in required_vars if not os.getenv(v)]
        
        if missing:
            raise ProviderConfigError(
                f"ODOO_PROVIDER_MODE=real but missing required config: {', '.join(missing)}"
            )
        
        client = OdooClient(
            base_url=os.getenv("ODOO_BASE_URL"),
            db=os.getenv("ODOO_DB"),
            username=os.getenv("ODOO_USERNAME"),
            api_key=os.getenv("ODOO_API_KEY"),
            timeout=int(os.getenv("ODOO_TIMEOUT", "30")),
            verify_ssl=os.getenv("ODOO_VERIFY_SSL", "true").lower() == "true",
        )
        return OdooRealProvider(client)
    
    raise ProviderConfigError(
        f"Invalid ODOO_PROVIDER_MODE: {provider_mode}. Must be 'mock' or 'real'."
    )
