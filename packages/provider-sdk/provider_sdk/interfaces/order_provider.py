from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from provider_sdk.dto.order_dto import OrderDTO


class OrderProvider(ABC):
    @abstractmethod
    def get_order(self, order_id: str) -> "OrderDTO":
        raise NotImplementedError

    @abstractmethod
    def get_platform(self) -> str:
        raise NotImplementedError