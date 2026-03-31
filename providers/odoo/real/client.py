from typing import Any
from xmlrpc.client import ServerProxy


class OdooClient:
    """Minimal Odoo XML-RPC client."""

    def __init__(
        self,
        base_url: str,
        db: str,
        username: str,
        api_key: str,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        self._base_url = base_url.rstrip("/")
        self._db = db
        self._username = username
        self._api_key = api_key
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        
        self._uid: int | None = None
        self._common: ServerProxy | None = None
        self._object: ServerProxy | None = None

    def authenticate(self) -> int:
        """Authenticate with Odoo and get UID."""
        self._common = ServerProxy(
            f"{self._base_url}/xmlrpc/2/common",
            allow_none=True
        )
        self._uid = self._common.authenticate(
            self._db, self._username, self._api_key, {}
        )
        if not self._uid:
            raise RuntimeError("Odoo authentication failed")
        
        self._object = ServerProxy(
            f"{self._base_url}/xmlrpc/2/object",
            allow_none=True
        )
        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        """Execute a method on an Odoo model."""
        if self._uid is None:
            self.authenticate()
        return self._object.execute_kw(
            self._db,
            self._uid,
            self._api_key,
            model,
            method,
            args or [],
            kwargs or {}
        )

    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict]:
        """Search and read records from an Odoo model."""
        kwargs = {}
        if domain is not None:
            kwargs["domain"] = domain
        if fields is not None:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", kwargs=kwargs)

    def close(self) -> None:
        """Close the Odoo client connection."""
        self._common = None
        self._object = None
        self._uid = None
