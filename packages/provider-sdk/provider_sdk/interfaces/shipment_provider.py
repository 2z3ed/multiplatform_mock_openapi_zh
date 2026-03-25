from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from provider_sdk.dto.shipment_dto import ShipmentDTO


class ShipmentProvider(ABC):
    @abstractmethod
    def get_shipment(self, order_id: str) -> "ShipmentDTO":
        raise NotImplementedError

    @abstractmethod
    def get_platform(self) -> str:
        raise NotImplementedError