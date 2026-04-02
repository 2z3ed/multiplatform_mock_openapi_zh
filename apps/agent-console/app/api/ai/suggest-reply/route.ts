import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const platformSimBody = {
      conversation_id: body.conversation_id,
      platform: body.platform || "jd",
      user_message: body.message || body.user_message || "",
      conversation_history: body.conversation_history || [],
    };
    const response = await fetch(`${API_GATEWAY_URL}/api/ai/suggest-reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(platformSimBody),
    });
    const data = await response.json();
    const suggestions = data.suggestions || [];
    return NextResponse.json({
      intent: body.platform === "jd" ? "ask_order_status" : "default",
      confidence: 0.85,
      suggested_reply: suggestions[0] || "您好，请问有什么可以帮您？",
      used_tools: [],
      risk_level: "low",
      needs_human_review: false,
    });
  } catch (error) {
    return NextResponse.json({ error: "Failed to get AI suggestion" }, { status: 500 });
  }
}
