"use client";

import { useState, useEffect } from "react";
import {
  CustomerProfile,
  getCustomerProfile,
} from "../../../lib/profile";
import {
  CustomerTag,
  getCustomerTags,
  createCustomerTag,
  deleteCustomerTag,
} from "../../../lib/customerTag";

interface CustomerProfilePanelProps {
  customerPk: number;
}

export default function CustomerProfilePanel({ customerPk }: CustomerProfilePanelProps) {
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [tags, setTags] = useState<CustomerTag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTagForm, setShowTagForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    fetchData();
  }, [customerPk]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [profileData, tagsData] = await Promise.all([
        getCustomerProfile(customerPk),
        getCustomerTags(customerPk),
      ]);
      setProfile(profileData);
      setTags(tagsData);
    } catch (err) {
      setError("客户画像加载失败");
      console.error("Failed to fetch customer data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTag = async (tagType: string, tagValue: string) => {
    try {
      setCreating(true);
      await createCustomerTag({
        customer_id: customerPk,
        tag_type: tagType,
        tag_value: tagValue,
      });
      setShowTagForm(false);
      await fetchData();
    } catch (err) {
      alert(`创建标签失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    try {
      setDeletingId(tagId);
      await deleteCustomerTag(tagId);
      await fetchData();
    } catch (err) {
      alert(`删除标签失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">客户画像</h3>
        <p className="text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">客户画像</h3>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-lg">客户画像</h3>
      </div>

      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">消费统计</h4>
        {profile ? (
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">订单数:</span>
              <span>{profile.total_orders}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">总消费:</span>
              <span>¥{profile.total_spent}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">平均订单:</span>
              <span>¥{profile.avg_order_value}</span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">暂无客户画像</p>
        )}
      </div>

      <div className="border-t pt-3">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium text-gray-700">标签</h4>
          <button
            onClick={() => setShowTagForm(!showTagForm)}
            className="text-xs text-blue-600 hover:underline"
          >
            {showTagForm ? "取消" : "+ 添加"}
          </button>
        </div>

        {showTagForm && (
          <TagCreateForm
            onSubmit={handleCreateTag}
            onCancel={() => setShowTagForm(false)}
            submitting={creating}
          />
        )}

        {tags.length === 0 && !showTagForm ? (
          <p className="text-sm text-gray-500">暂无标签</p>
        ) : (
          <div className="space-y-2">
            {tags.map((tag) => (
              <div key={tag.id} className="flex justify-between items-center bg-gray-50 rounded px-2 py-1">
                <div>
                  <span className="text-sm font-medium">{tag.tag_value}</span>
                  <span className="text-xs text-gray-500 ml-1">({tag.tag_type})</span>
                </div>
                <button
                  onClick={() => handleDeleteTag(tag.id)}
                  disabled={deletingId === tag.id}
                  className="text-xs text-red-600 hover:underline disabled:opacity-50"
                >
                  {deletingId === tag.id ? "删除中..." : "删除"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TagCreateForm({
  onSubmit,
  onCancel,
  submitting,
}: {
  onSubmit: (tagType: string, tagValue: string) => void;
  onCancel: () => void;
  submitting: boolean;
}) {
  const [tagType, setTagType] = useState("intent");
  const [tagValue, setTagValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!tagValue.trim()) return;
    onSubmit(tagType, tagValue.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="border rounded p-2 mb-2 bg-gray-50">
      <div className="mb-2">
        <label className="block text-xs text-gray-500 mb-1">标签类型</label>
        <select
          value={tagType}
          onChange={(e) => setTagType(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
        >
          <option value="intent">意向</option>
          <option value="preference">偏好</option>
          <option value="transaction">交易</option>
          <option value="risk">风险</option>
        </select>
      </div>
      <div className="mb-2">
        <label className="block text-xs text-gray-500 mb-1">标签值</label>
        <input
          type="text"
          value={tagValue}
          onChange={(e) => setTagValue(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
          placeholder="输入标签值"
        />
      </div>
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting || !tagValue.trim()}
          className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {submitting ? "创建中..." : "创建"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600"
        >
          取消
        </button>
      </div>
    </form>
  );
}
