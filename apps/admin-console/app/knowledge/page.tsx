"use client";

import { useState } from "react";

interface Document {
  document_id: string;
  title: string;
  doc_type: string;
  chunk_count: number;
  created_at: string;
}

const mockDocuments: Document[] = [
  {
    document_id: "doc_001",
    title: "订单查询FAQ",
    doc_type: "faq",
    chunk_count: 5,
    created_at: "2024-03-15T10:00:00Z",
  },
  {
    document_id: "doc_002",
    title: "退货流程说明",
    doc_type: "sop",
    chunk_count: 8,
    created_at: "2024-03-16T10:00:00Z",
  },
];

const docTypeLabels: Record<string, string> = {
  faq: "常见问题",
  sop: "标准流程",
  product: "商品知识",
};

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>(mockDocuments);
  const [showUpload, setShowUpload] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleUpload = () => {
    if (title && content) {
      const newDoc: Document = {
        document_id: `doc_${Date.now()}`,
        title,
        doc_type: "faq",
        chunk_count: content.split(".").length,
        created_at: new Date().toISOString(),
      };
      setDocuments([...documents, newDoc]);
      setShowUpload(false);
      setTitle("");
      setContent("");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">知识库管理</h1>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            上传文档
          </button>
        </div>
      </header>

      {showUpload && (
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">上传新文档</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">标题</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="输入文档标题"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">内容</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={6}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="输入文档内容"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleUpload}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  上传
                </button>
                <button
                  onClick={() => setShowUpload(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">标题</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunk数</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">{doc.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {docTypeLabels[doc.doc_type] || doc.doc_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{doc.chunk_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleString("zh-CN")}
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