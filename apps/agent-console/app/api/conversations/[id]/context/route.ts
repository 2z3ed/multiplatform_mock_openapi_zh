import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const response = await fetch(`${API_GATEWAY_URL}/api/conversations/${id}/context`, {
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      return NextResponse.json({ error: `Backend returned ${response.status}` }, { status: response.status });
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch conversation context" }, { status: 500 });
  }
}
