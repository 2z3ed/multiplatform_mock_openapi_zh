export default function PageError({ error, onRetry }: { error: { message: string }; onRetry: () => void }) {
  return (
    <div className="h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md p-8">
        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h2 className="text-xl font-medium text-gray-800 mb-2">加载失败</h2>
        <p className="text-sm text-gray-500 mb-6">{error.message}</p>
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          重试
        </button>
      </div>
    </div>
  );
}
