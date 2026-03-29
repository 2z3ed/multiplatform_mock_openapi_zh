import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request, { params }: { params: Promise<{ platform: string; afterSaleId: string }> }) {
  try {
    const { platform, afterSaleId } = await params;
    const response = await fetch(`${API_GATEWAY_URL}/api/after-sales/${platform}/${afterSaleId}`, {
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch after-sales" }, { status: 500 });
  }
}
