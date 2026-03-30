import Link from "next/link";

const menuItems = [
  { href: "/platforms", label: "平台配置", description: "管理平台账户和 Provider 模式" },
  { href: "/knowledge", label: "知识库管理", description: "管理知识库文档和索引" },
  { href: "/audit", label: "审计日志", description: "查看系统操作日志" },
  { href: "/operations", label: "运营活动", description: "查看运营活动列表" },
  { href: "/analytics", label: "数据概览", description: "查看数据统计摘要" },
  { href: "/quality/rules", label: "质检规则", description: "管理质检规则" },
  { href: "/quality/results", label: "质检结果", description: "查看质检结果列表" },
  { href: "/quality/alerts", label: "质检告警", description: "查看质检告警列表" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <h1 className="text-xl font-bold">管理后台</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <h2 className="text-lg font-medium mb-4">功能入口</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <h3 className="text-lg font-medium text-blue-600">{item.label}</h3>
              <p className="mt-1 text-sm text-gray-500">{item.description}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
