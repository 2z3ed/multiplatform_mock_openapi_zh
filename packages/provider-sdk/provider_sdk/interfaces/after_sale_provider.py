from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from provider_sdk.dto.after_sale_dto import AfterSaleDTO


class AfterSaleProvider(ABC):
    @abstractmethod
    def get_after_sale(self, after_sale_id: str) -> "AfterSaleDTO":
        raise NotImplementedError

    @abstractmethod
    def get_platform(self) -> str:
        raise NotImplementedError