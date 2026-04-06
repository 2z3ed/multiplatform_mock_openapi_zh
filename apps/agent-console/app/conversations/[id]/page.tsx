"use client";

import { useParams } from "next/navigation";
import ConversationHeader from "./components/ConversationHeader";
import MessageStream from "./components/MessageStream";
import ReplyComposer from "./components/ReplyComposer";
import OrderPanel from "./components/OrderPanel";
import ShipmentPanel from "./components/ShipmentPanel";
import AfterSalePanel from "./components/AfterSalePanel";
import InventoryPanel from "./components/InventoryPanel";
import SuggestionPanel from "./components/SuggestionPanel";
import FollowupPanel from "./components/FollowupPanel";
import RecommendationPanel from "./components/RecommendationPanel";
import RiskFlagPanel from "./components/RiskFlagPanel";
import CustomerProfilePanel from "./components/CustomerProfilePanel";
import QualityInspectionPanel from "./components/QualityInspectionPanel";
import PageLoading from "./components/PageLoading";
import PageError from "./components/PageError";
import { useConversationFlow } from "./hooks/useConversationFlow";

export default function ConversationDetailPage() {
  const params = useParams();
  const convId = params.id as string;
  const {
    conversation,
    messages,
    context,
    suggestion,
    suggestionStatus,
    replyText,
    setReplyText,
    loading,
    fetchError,
    isSending,
    waitingForReply,
    hasTimedOut,
    newMessageId,
    handleSend,
    handleApplySuggestion,
    handleGenerateSuggestion,
    retry,
  } = useConversationFlow(convId);

  if (loading) return <PageLoading />;
  if (fetchError) return <PageError error={fetchError} onRetry={retry} />;
  if (!conversation) return <PageError error={{ message: "会话不存在" }} onRetry={retry} />;

  const firstOrder = context?.orders?.[0] || null;
  const orderData = firstOrder?.order || null;
  const shipmentData = firstOrder?.shipment || null;
  const afterSalesData = firstOrder?.after_sales || [];
  const inventoryData = firstOrder?.inventory || null;
  const platform = firstOrder?.platform || conversation.platform;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <ConversationHeader conversation={conversation} />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <MessageStream messages={messages} waiting={waitingForReply} hasTimedOut={hasTimedOut} newMessageId={newMessageId} />
          <ReplyComposer onSend={handleSend} initialText={replyText} isSending={isSending} />
        </div>
        <div className="w-80 border-l bg-gray-100 p-4 space-y-4 overflow-y-auto">
          <OrderPanel order={orderData} platform={platform} />
          <ShipmentPanel shipment={shipmentData} platform={platform} />
          <AfterSalePanel afterSales={afterSalesData} platform={platform} />
          <InventoryPanel inventory={inventoryData} platform={platform} />
          <SuggestionPanel
            suggestion={suggestion}
            status={suggestionStatus}
            onApply={handleApplySuggestion}
            onGenerate={handleGenerateSuggestion}
          />
          {conversation?.conversation_pk && (
            <FollowupPanel conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.conversation_pk && (
            <RecommendationPanel conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.customer_pk && (
            <RiskFlagPanel customerPk={conversation.customer_pk} conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.customer_pk && (
            <CustomerProfilePanel customerPk={conversation.customer_pk} />
          )}
          {conversation?.conversation_pk && (
            <QualityInspectionPanel conversationPk={conversation.conversation_pk} />
          )}
        </div>
      </div>
    </div>
  );
}
