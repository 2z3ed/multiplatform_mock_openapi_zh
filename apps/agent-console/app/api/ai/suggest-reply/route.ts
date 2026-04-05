import { NextResponse } from "next/server";

const AI_ORCHESTRATOR_URL = "http://localhost:8002";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch(`${AI_ORCHESTRATOR_URL}/api/ai/suggest-reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: body.conversation_id,
        message: body.message || body.user_message || "",
        platform: body.platform || "jd",
      }),
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: "Failed to get AI suggestion" }, { status: 500 });
  }
}
