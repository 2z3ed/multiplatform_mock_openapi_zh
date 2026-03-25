from abc import ABC, abstractmethod


class MessageProvider(ABC):
    @abstractmethod
    def sync_messages(self) -> object:
        raise NotImplementedError
