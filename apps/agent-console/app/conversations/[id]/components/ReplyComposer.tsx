import { useState, useEffect } from "react";

export default function ReplyComposer({
  onSend,
  initialText,
}: {
  onSend: (text: string) => void;
  initialText?: string;
}) {
  const [text, setText] = useState(initialText || "");

  useEffect(() => {
    setText(initialText || "");
  }, [initialText]);

  return (
    <div className="border-t p-4 bg-white">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="输入回复内容..."
        className="w-full border rounded-lg p-3 min-h-[100px]"
      />
      <div className="mt-2 flex justify-end">
        <button
          onClick={() => {
            if (text.trim()) {
              onSend(text);
              setText("");
            }
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          发送
        </button>
      </div>
    </div>
  );
}
