import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const conversationId = searchParams.get("conversation_id");
    const url = `${API_GATEWAY_URL}/api/quality/results${conversationId ? `?conversation_id=${conversationId}` : ""}`;
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      return NextResponse.json({ error: `Backend returned ${response.status}` }, { status: response.status });
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch quality results" }, { status: 500 });
  }
}
