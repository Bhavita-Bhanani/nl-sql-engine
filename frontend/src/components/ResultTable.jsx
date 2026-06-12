import { useState } from "react";

const PAGE_SIZE = 10;

function exportCSV(results) {
  if (!results?.length) return;
  const headers = Object.keys(results[0]);
  const rows = results.map((r) => headers.map((h) => JSON.stringify(r[h] ?? "")).join(","));
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "query_results.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export default function ResultTable({ results }) {
  const [page, setPage] = useState(0);

  if (!results?.length)
    return (
      <div className="text-gray-600 text-sm py-12 text-center flex flex-col items-center gap-2">
        <svg className="h-10 w-10 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0H4" />
        </svg>
        No results to display.
      </div>
    );

  const columns = Object.keys(results[0]);
  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const pageData = results.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          <span className="text-purple-400 font-semibold">{results.length}</span> row{results.length !== 1 ? "s" : ""} returned
        </span>
        <button
          onClick={() => exportCSV(results)}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-purple-300 glass px-3 py-1.5 rounded-lg transition-all hover:border-purple-500/30"
        >
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/[0.06]">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ background: "rgba(139,92,246,0.1)" }}>
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 text-left text-xs font-bold text-purple-300 uppercase tracking-wider whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.map((row, i) => (
              <tr
                key={i}
                className="border-t border-white/[0.04] transition-colors"
                style={{ background: i % 2 === 0 ? "rgba(255,255,255,0.02)" : "transparent" }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(139,92,246,0.07)"}
                onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "rgba(255,255,255,0.02)" : "transparent"}
              >
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2.5 text-gray-300 whitespace-nowrap max-w-xs truncate">
                    {row[col] == null ? (
                      <span className="text-gray-700 italic text-xs">null</span>
                    ) : typeof row[col] === "number" ? (
                      <span className="text-emerald-400 font-mono font-medium">{row[col]}</span>
                    ) : (
                      String(row[col])
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>Page {page + 1} of {totalPages}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
              className="px-3 py-1.5 glass rounded-lg disabled:opacity-30 hover:border-purple-500/30 transition-all text-gray-400">
              ← Prev
            </button>
            <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1}
              className="px-3 py-1.5 glass rounded-lg disabled:opacity-30 hover:border-purple-500/30 transition-all text-gray-400">
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
