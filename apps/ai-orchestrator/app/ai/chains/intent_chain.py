"""Intent classification chain."""

from typing import Literal

IntentType = Literal["faq", "order_query", "shipment_query", "after_sale_query", "unknown"]


class IntentClassifier:
    def __init__(self):
        self.keywords = {
            "order_query": ["订单", "订单号", "下单", "买", "订单状态"],
            "shipment_query": ["物流", "快递", "发货", "运输", "到哪了", "追踪"],
            "after_sale_query": ["退款", "退货", "售后", "取消订单", "退货"],
            "faq": ["怎么", "如何", "请问", "是什么", "哪里", "多少"]
        }

    def classify(self, message: str) -> dict:
        message_lower = message.lower()
        
        for intent, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    confidence = 0.8 if len(message) > 10 else 0.6
                    return {
                        "intent": intent,
                        "confidence": confidence,
                        "reason": f"keyword match: {keyword}"
                    }
        
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "reason": "no keywords matched"
        }


def classify_intent(message: str) -> dict:
    classifier = IntentClassifier()
    return classifier.classify(message)