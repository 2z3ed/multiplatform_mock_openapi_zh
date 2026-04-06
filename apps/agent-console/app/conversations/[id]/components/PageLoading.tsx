export default function PageLoading() {
  return (
    <div className="h-screen flex flex-col bg-gray-50 animate-pulse">
      <div className="bg-white border-b px-6 py-4">
        <div className="h-6 bg-gray-200 rounded w-48 mb-2"></div>
        <div className="h-4 bg-gray-100 rounded w-64"></div>
      </div>
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col p-6 space-y-4">
          <div className="self-start h-16 bg-gray-200 rounded-lg w-64"></div>
          <div className="self-end h-16 bg-gray-100 rounded-lg w-48"></div>
          <div className="self-start h-16 bg-gray-200 rounded-lg w-56"></div>
          <div className="self-end h-16 bg-gray-100 rounded-lg w-40"></div>
          <div className="self-start h-16 bg-gray-200 rounded-lg w-72"></div>
        </div>
        <div className="w-80 border-l bg-gray-100 p-4 space-y-4">
          <div className="h-32 bg-gray-200 rounded-lg"></div>
          <div className="h-32 bg-gray-200 rounded-lg"></div>
          <div className="h-32 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    </div>
  );
}
