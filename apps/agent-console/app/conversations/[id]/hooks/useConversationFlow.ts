import { useState, useEffect, useRef, useCallback } from "react";
import type { Message, Conversation, ConversationContext, AISuggestion, SuggestionStatus } from "../types";
import { autoEvaluateFollowup } from "../../../lib/followup";
import { autoEvaluateRecommendation } from "../../../lib/recommendation";
import { autoEvaluateRisk } from "../../../lib/riskFlag";
import { autoEvaluateQuality } from "../../../lib/quality";

const POLL_INTERVAL_MS = 2000;
const POLL_MAX_ATTEMPTS = 5;
const SUGGESTION_TIMEOUT_MS = 15000;

interface UseConversationFlowResult {
  conversation: Conversation | null;
  messages: Message[];
  context: ConversationContext | null;
  suggestion: AISuggestion | null;
  suggestionStatus: SuggestionStatus;
  replyText: string;
  setReplyText: (t: string) => void;
  loading: boolean;
  fetchError: { message: string } | null;
  isSending: boolean;
  waitingForReply: boolean;
  hasTimedOut: boolean;
  newMessageId: string | null;
  handleSend: (text: string) => Promise<void>;
  handleApplySuggestion: (text: string) => void;
  handleGenerateSuggestion: () => Promise<void>;
  retry: () => void;
}

export function useConversationFlow(convId: string): UseConversationFlowResult {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [context, setContext] = useState<ConversationContext | null>(null);
  const [suggestion, setSuggestion] = useState<AISuggestion | null>(null);
  const [suggestionStatus, setSuggestionStatus] = useState<SuggestionStatus>({ type: "idle" });
  const [replyText, setReplyText] = useState("");
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<{ message: string } | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [waitingForReply, setWaitingForReply] = useState(false);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [newMessageId, setNewMessageId] = useState<string | null>(null);
  const evaluatedRef = useRef(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollAttemptRef = useRef(0);
  const lastInboundCountRef = useRef(0);
  const isGeneratingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const highlightTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchMessages = useCallback(async (): Promise<number> => {
    try {
      const res = await fetch(`/api/conversations/${convId}/messages`);
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        const inboundItems = items.filter((m: Message) => m.direction === "inbound");
        const inboundCount = inboundItems.length;
        if (inboundCount > lastInboundCountRef.current) {
          const newMsg = inboundItems[inboundItems.length - 1];
          setNewMessageId(newMsg.id);
          if (highlightTimerRef.current) clearTimeout(highlightTimerRef.current);
          highlightTimerRef.current = setTimeout(() => setNewMessageId(null), 3000);

          stopPolling();
          setWaitingForReply(false);
          setHasTimedOut(false);
          await refreshSuggestion(items);
        }
        lastInboundCountRef.current = inboundCount;
        setMessages(items);
        return inboundCount;
      }
    } catch (error) {
      console.error("Failed to fetch messages:", error);
    }
    return lastInboundCountRef.current;
  }, [convId]);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    pollAttemptRef.current = 0;
  }, []);

  const startPolling = useCallback(() => {
    stopPolling();
    lastInboundCountRef.current = messages.filter((m) => m.direction === "inbound").length;
    pollAttemptRef.current = 0;
    setWaitingForReply(true);
    setHasTimedOut(false);
    pollingRef.current = setInterval(() => {
      pollAttemptRef.current += 1;
      if (pollAttemptRef.current >= POLL_MAX_ATTEMPTS) {
        stopPolling();
        setWaitingForReply(false);
        setHasTimedOut(true);
        return;
      }
      fetchMessages();
    }, POLL_INTERVAL_MS);
  }, [messages, fetchMessages, stopPolling]);

  const generateSuggestion = useCallback(async (trigger: "manual" | "auto", currentMessages: Message[]) => {
    if (isGeneratingRef.current) return;
    isGeneratingRef.current = true;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setSuggestionStatus({ type: "loading" });

    try {
      const lastInbound = currentMessages.filter((m) => m.direction === "inbound").pop();
      if (!lastInbound) {
        setSuggestionStatus({ type: "empty" });
        isGeneratingRef.current = false;
        return;
      }

      const timeoutId = setTimeout(() => {
        abortControllerRef.current?.abort();
      }, SUGGESTION_TIMEOUT_MS);

      const res = await fetch(`/api/ai/suggest-reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: convId,
          message: lastInbound.content,
          platform: conversation?.platform || "jd",
        }),
        signal: abortControllerRef.current.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        if (trigger === "auto" && suggestion) {
          setSuggestionStatus({ type: "error", message: "自动刷新失败，已保留上一版建议" });
        } else {
          setSuggestionStatus({ type: "error", message: `请求失败 (${res.status})` });
        }
        isGeneratingRef.current = false;
        return;
      }

      const data = await res.json();

      if (!data || !data.suggested_reply) {
        if (trigger === "auto" && suggestion) {
          setSuggestionStatus({ type: "error", message: "自动刷新未返回新建议，已保留上一版" });
        } else {
          setSuggestionStatus({ type: "empty" });
          setSuggestion(null);
        }
        isGeneratingRef.current = false;
        return;
      }

      if (data.degraded === true) {
        setSuggestionStatus({ type: "degraded", reason: data.fallback_reason || undefined });
        setSuggestion(data);
        isGeneratingRef.current = false;
        return;
      }

      setSuggestionStatus({ type: "success" });
      setSuggestion(data);
    } catch (error: unknown) {
      const isAbort = error instanceof DOMException && error.name === "AbortError";
      if (isAbort) return;

      if (trigger === "auto" && suggestion) {
        setSuggestionStatus({ type: "error", message: "自动刷新失败，已保留上一版建议" });
      } else {
        setSuggestionStatus({ type: "error", message: error instanceof Error ? error.message : "生成建议时发生错误" });
        setSuggestion(null);
      }
    } finally {
      isGeneratingRef.current = false;
    }
  }, [convId, conversation?.platform, suggestion]);

  const refreshSuggestion = useCallback(async (currentMessages: Message[]) => {
    await generateSuggestion("auto", currentMessages);
  }, [generateSuggestion]);

  const loadInitialData = useCallback(async () => {
    setLoading(true);
    setFetchError(null);
    evaluatedRef.current = false;
    try {
      const [convRes, msgRes, ctxRes] = await Promise.all([
        fetch(`/api/conversations/${convId}`),
        fetch(`/api/conversations/${convId}/messages`),
        fetch(`/api/conversations/${convId}/context`),
      ]);

      if (!convRes.ok) {
        if (convRes.status === 404) {
          setFetchError({ message: "会话不存在" });
        } else {
          setFetchError({ message: `加载失败 (${convRes.status})，请稍后重试` });
        }
        return;
      }

      if (!msgRes.ok) {
        setFetchError({ message: `加载消息失败 (${msgRes.status})，请稍后重试` });
        return;
      }

      const convData = await convRes.json();
      const msgData = await msgRes.json();
      setConversation(convData);
      setMessages(msgData.items || []);
      lastInboundCountRef.current = (msgData.items || []).filter((m: Message) => m.direction === "inbound").length;
      if (ctxRes.ok) {
        setContext(await ctxRes.json());
      } else {
        setContext(null);
      }
    } catch (error) {
      setFetchError({ message: error instanceof Error ? error.message : "网络错误，请稍后重试" });
    } finally {
      setLoading(false);
    }
  }, [convId]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const retry = useCallback(() => {
    loadInitialData();
  }, [loadInitialData]);

  useEffect(() => {
    if (!context || !conversation) return;
    const customerId = conversation.customer_pk;
    const convIdStr = String(conversation.conversation_pk || convId);
    const evaluations = [];
    if (customerId) {
      evaluations.push(
        autoEvaluateFollowup(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate followup failed:", e)),
        autoEvaluateRecommendation(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate recommendation failed:", e)),
        autoEvaluateRisk(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate risk failed:", e)),
      );
    }
    evaluations.push(
      autoEvaluateQuality(convIdStr).catch((e) => console.warn("Auto-evaluate quality failed:", e)),
    );
    Promise.allSettled(evaluations);
  }, [context, conversation, convId]);

  useEffect(() => {
    return () => {
      stopPolling();
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (highlightTimerRef.current) {
        clearTimeout(highlightTimerRef.current);
      }
    };
  }, [stopPolling]);

  const handleSend = async (text: string) => {
    setIsSending(true);
    setHasTimedOut(false);
    try {
      const response = await fetch(`/api/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: convId,
          content: text,
          sender_type: "agent",
          sender_id: "agent_001",
        }),
      });
      if (response.ok) {
        const inboundCount = await fetchMessages();
        if (inboundCount > lastInboundCountRef.current) {
          setWaitingForReply(false);
          stopPolling();
          const currentMessages = messages;
          await refreshSuggestion(currentMessages);
          return;
        }
        startPolling();
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsSending(false);
    }
  };

  const handleApplySuggestion = (text: string) => {
    setReplyText(text);
  };

  const handleGenerateSuggestion = async () => {
    await generateSuggestion("manual", messages);
  };

  return {
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
  };
}
