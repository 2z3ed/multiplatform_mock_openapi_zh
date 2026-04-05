"""Provider SDK exceptions."""


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ResourceNotFoundError(ProviderError):
    """Raised when a requested resource is not found.

    Maps to HTTP 404.
    """
    def __init__(self, resource_type: str, resource_id: str, platform: str = ""):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.platform = platform
        msg = f"{resource_type} not found: {resource_id}"
        if platform:
            msg = f"{resource_type} not found on {platform}: {resource_id}"
        super().__init__(msg)


class ServiceUnavailableError(ProviderError):
    """Raised when an upstream service is unavailable.

    Maps to HTTP 503.
    """
    def __init__(self, service: str, detail: str = ""):
        self.service = service
        self.detail = detail
        msg = f"Service unavailable: {service}"
        if detail:
            msg = f"{msg} ({detail})"
        super().__init__(msg)
