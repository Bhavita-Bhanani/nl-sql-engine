import axios from "axios";
import api from "../api.js";

export default function QueryHistory({ history, onRerun, onRefresh }) {
  if (!history?.length)
    return (
      <div className="text-gray-700 text-sm py-6 text-center">
        No queries yet — ask something above!
      </div>
    );

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await api.delete(`/history/${id}`);
      onRefresh();
    } catch {}
  };

  return (
    <div className="space-y-2">
      {history.map((entry) => (
        <div
          key={entry.id}
          onClick={() => onRerun(entry.question)}
          className="group flex items-start justify-between gap-3 px-4 py-3 rounded-xl glass glass-hover cursor-pointer transition-all"
        >
          <div className="flex items-start gap-3 min-w-0">
            <span className={`mt-1.5 flex-shrink-0 h-2 w-2 rounded-full ${entry.success ? "bg-emerald-500 shadow-[0_0_6px_rgba(52,211,153,0.6)]" : "bg-red-500"}`} />
            <div className="min-w-0">
              <p className="text-sm text-gray-300 truncate group-hover:text-white transition-colors">{entry.question}</p>
              <p className="text-xs text-gray-600 mt-0.5">
                {entry.success
                  ? <><span className="text-purple-500">{entry.result_count} rows</span> · {entry.execution_time_ms}ms</>
                  : <span className="text-red-500">Failed</span>
                }
                {" · "}{entry.created_at ? new Date(entry.created_at).toLocaleTimeString() : ""}
              </p>
            </div>
          </div>
          <button
            onClick={(e) => handleDelete(entry.id, e)}
            className="flex-shrink-0 opacity-0 group-hover:opacity-100 text-gray-700 hover:text-red-400 transition-all p-1 rounded-lg"
          >
            <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
