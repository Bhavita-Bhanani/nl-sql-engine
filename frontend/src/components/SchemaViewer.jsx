import { useState } from "react";

function typeColor(type) {
  const t = (type || "").toUpperCase();
  if (t.includes("INT")) return "#34d399";
  if (t.includes("REAL") || t.includes("FLOAT") || t.includes("NUMERIC")) return "#fb923c";
  if (t.includes("TEXT") || t.includes("CHAR") || t.includes("CLOB")) return "#60a5fa";
  if (t.includes("BLOB")) return "#c084fc";
  if (t.includes("DATE") || t.includes("TIME")) return "#f9a8d4";
  return "#9ca3af";
}

export default function SchemaViewer({ schema, loading }) {
  const [openTables, setOpenTables] = useState({});
  const toggle = (t) => setOpenTables(p => ({ ...p, [t]: !p[t] }));

  if (loading)
    return (
      <div className="p-4 space-y-3">
        {[1,2,3].map(i => (
          <div key={i} className="h-8 rounded-lg bg-white/[0.04] animate-pulse" />
        ))}
      </div>
    );

  if (!schema?.length)
    return <div className="p-4 text-gray-600 text-xs text-center">No schema loaded.</div>;

  return (
    <div className="p-3 space-y-1">
      <p className="text-xs text-gray-600 uppercase tracking-widest mb-3 px-1 font-semibold">
        {schema.length} tables
      </p>
      {schema.map(({ table, row_count, columns }) => (
        <div key={table}>
          <button
            onClick={() => toggle(table)}
            className="w-full flex items-center justify-between text-left px-3 py-2 rounded-xl glass-hover transition-all"
          >
            <div className="flex items-center gap-2">
              <span className="text-purple-500 text-xs">{openTables[table] ? "▾" : "▸"}</span>
              <span className="text-sm font-semibold text-gray-200">{table}</span>
            </div>
            <span className="text-xs text-gray-600 font-mono">{row_count}</span>
          </button>

          {openTables[table] && (
            <div className="ml-5 mt-1 mb-1 pl-3 border-l border-purple-900/50 space-y-0.5">
              {columns.map((col) => (
                <div key={col.name} className="flex items-center justify-between py-0.5 px-1">
                  <div className="flex items-center gap-1.5">
                    {col.primary_key && <span className="text-yellow-500 text-xs">⬡</span>}
                    <span className="text-xs text-gray-400">{col.name}</span>
                  </div>
                  <span className="text-xs font-mono" style={{ color: typeColor(col.type) }}>
                    {col.type || "?"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
