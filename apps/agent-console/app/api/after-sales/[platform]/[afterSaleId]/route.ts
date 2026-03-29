import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request, { params }: { params: { platform: string; afterSaleId: string } }) {
  try {
    const response = await fetch(`${API_GATEWAY_URL}/api/after-sales/${params.platform}/${params.afterSaleId}`, {
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch after-sales" }, { status: 500 });
  }
}
