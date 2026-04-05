"""Helper for provider HTTP calls with proper error handling."""
import httpx
from provider_sdk.exceptions import ResourceNotFoundError, ServiceUnavailableError


def _handle_response(response: httpx.Response, resource_type: str, resource_id: str, platform: str):
    """Handle HTTP response from official-sim.

    - 404 -> ResourceNotFoundError
    - 5xx -> ServiceUnavailableError
    - 200 -> return parsed JSON
    - other -> let httpx.raise_for_status() handle it
    """
    if response.status_code == 404:
        detail = response.json().get("detail", "") if response.headers.get("content-type", "").startswith("application/json") else ""
        raise ResourceNotFoundError(resource_type, resource_id, platform)
    if response.status_code >= 500:
        detail = ""
        try:
            detail = response.json().get("detail", "")
        except Exception:
            pass
        raise ServiceUnavailableError("official-sim", detail)
    response.raise_for_status()
    return response.json()
