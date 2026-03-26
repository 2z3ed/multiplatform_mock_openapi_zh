"use client";

import { useState, useEffect } from "react";

interface PlatformAccount {
  id: string;
  platform: string;
  account_name: string;
  provider_mode: "mock" | "real";
  status: "active" | "inactive";
  last_sync: string;
}

const platformLabels: Record<string, string> = {
  jd: "京东",
  douyin_shop: "抖音店铺",
  wecom_kf: "企微客服",
};

export default function PlatformsPage() {
  const [platforms, setPlatforms] = useState<PlatformAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPlatforms() {
      try {
        const res = await fetch("/api/platform-accounts");
        const data = await res.json();
        setPlatforms(data.items || []);
      } catch (error) {
        console.error("Failed to fetch platforms:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchPlatforms();
  }, []);

  const toggleProviderMode = async (id: string) => {
    try {
      const res = await fetch("/api/platform-accounts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, action: "switch_mode" }),
      });
      const data = await res.json();
      if (data.platform) {
        setPlatforms(platforms.map(p => p.id === id ? data.platform : p));
      }
    } catch (error) {
      console.error("Failed to switch mode:", error);
    }
  };

  if (loading) return <div className="p-8 text-center">加载中...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <h1 className="text-xl font-bold">平台配置</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">平台</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">账户名称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider模式</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后同步</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {platforms.map((platform) => (
                <tr key={platform.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {platformLabels[platform.platform] || platform.platform}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{platform.account_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        platform.provider_mode === "mock"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-purple-100 text-purple-800"
                      }`}
                    >
                      {platform.provider_mode === "mock" ? "Mock" : "Real"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        platform.status === "active"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {platform.status === "active" ? "启用" : "停用"}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {platform.last_sync ? new Date(platform.last_sync).toLocaleString("zh-CN") : "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => toggleProviderMode(platform.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      切换模式
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}