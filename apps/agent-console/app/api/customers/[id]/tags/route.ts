import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const response = await fetch(`${API_GATEWAY_URL}/api/customers/${params.id}/tags`, {
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch customer tags" }, { status: 500 });
  }
}
