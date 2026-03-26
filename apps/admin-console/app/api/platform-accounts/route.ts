import { NextResponse } from "next/server";

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

let mockPlatformAccounts = [
  { id: "pa_001", platform: "jd", account_name: "京东旗舰店", provider_mode: "mock", status: "active", last_sync: "2024-03-20T10:00:00Z" },
  { id: "pa_002", platform: "douyin_shop", account_name: "抖音商城", provider_mode: "mock", status: "active", last_sync: "2024-03-20T10:00:00Z" },
  { id: "pa_003", platform: "wecom_kf", account_name: "企微客服", provider_mode: "mock", status: "active", last_sync: "2024-03-20T10:00:00Z" },
];

export async function GET() {
  return NextResponse.json({ items: mockPlatformAccounts });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { id, action } = body;
    
    if (action === "switch_mode") {
      mockPlatformAccounts = mockPlatformAccounts.map(p => 
        p.id === id 
          ? { ...p, provider_mode: p.provider_mode === "mock" ? "real" : "mock" }
          : p
      );
      
      const platform = mockPlatformAccounts.find(p => p.id === id);
      
      await fetch(`${API_GATEWAY_URL}/api/audit-logs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "provider_mode_switched",
          actor_type: "admin",
          actor_id: "admin_user",
          target_type: "platform",
          target_id: platform?.platform,
          detail: `Switched ${platform?.account_name} from mock to ${platform?.provider_mode}`,
          detail_json: { old_mode: "mock", new_mode: platform?.provider_mode },
        }),
      });
      
      return NextResponse.json({ status: "ok", platform: mockPlatformAccounts.find(p => p.id === id) });
    }
    
    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 });
  }
}