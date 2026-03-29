import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request, { params }: { params: Promise<{ platform: string; orderId: string }> }) {
  try {
    const { platform, orderId } = await params;
    const response = await fetch(`${API_GATEWAY_URL}/api/shipments/${platform}/${orderId}`, {
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch shipments" }, { status: 500 });
  }
}
