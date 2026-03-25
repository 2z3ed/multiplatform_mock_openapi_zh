from dataclasses import dataclass


@dataclass
class MessageDTO:
    platform: str
    conversation_id: str
    content: str
