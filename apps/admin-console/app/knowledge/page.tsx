"use client";

import { useState, useEffect } from "react";

interface Document {
  document_id: string;
  title: string;
  doc_type: string;
  chunk_count: number;
  created_at: string;
}

const docTypeLabels: Record<string, string> = {
  faq: "常见问题",
  sop: "标准流程",
  product: "商品知识",
};

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [reindexing, setReindexing] = useState(false);

  useEffect(() => {
    setLoading(false);
  }, []);

  const handleUpload = async () => {
    if (title && content) {
      try {
        const res = await fetch("/api/kb/documents", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, content, doc_type: "faq" }),
        });
        const data = await res.json();
        
        const newDoc: Document = {
          document_id: data.document_id,
          title,
          doc_type: data.doc_type,
          chunk_count: data.chunk_count,
          created_at: data.created_at,
        };
        setDocuments([...documents, newDoc]);
        setShowUpload(false);
        setTitle("");
        setContent("");
      } catch (error) {
        console.error("Failed to upload document:", error);
      }
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    try {
      await fetch("/api/kb/reindex", { method: "POST" });
      alert("重建索引完成");
    } catch (error) {
      console.error("Failed to reindex:", error);
    } finally {
      setReindexing(false);
    }
  };

  if (loading) return <div className="p-8 text-center">加载中...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">知识库管理</h1>
          <div className="flex gap-2">
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
            >
              {reindexing ? "重建中..." : "重建索引"}
            </button>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              上传文档
            </button>
          </div>
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
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    暂无文档，请上传
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.document_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">{doc.title}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        {docTypeLabels[doc.doc_type] || doc.doc_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{doc.chunk_count}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.created_at ? new Date(doc.created_at).toLocaleString("zh-CN") : "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}