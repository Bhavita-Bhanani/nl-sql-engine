import { useState } from "react";

const SQL_KEYWORDS = [
  "SELECT","FROM","WHERE","JOIN","LEFT","RIGHT","INNER","OUTER","ON",
  "GROUP BY","ORDER BY","HAVING","LIMIT","OFFSET","AS","AND","OR","NOT",
  "IN","LIKE","BETWEEN","IS","NULL","COUNT","SUM","AVG","MAX","MIN",
  "DISTINCT","WITH","UNION","BY","ASC","DESC","CASE","WHEN","THEN",
  "ELSE","END","COALESCE","CAST","ROUND","STRFTIME","DATE",
];

function highlightSQL(sql) {
  if (!sql) return "";
  const tokens = sql.split(/(\s+|[(),;])/);
  return tokens.map((token) => {
    const upper = token.toUpperCase().trim();
    if (SQL_KEYWORDS.includes(upper))
      return `<span style="color:#c084fc;font-weight:600">${token}</span>`;
    if (/^'[^']*'$/.test(token) || /^"[^"]*"$/.test(token))
      return `<span style="color:#34d399">${token}</span>`;
    if (/^\d+(\.\d+)?$/.test(token))
      return `<span style="color:#fb923c">${token}</span>`;
    return token;
  }).join("");
}

export default function SQLDisplay({ sql, executionTime }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!sql) return;
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!sql)
    return (
      <div className="text-gray-600 text-sm py-12 text-center">
        No SQL generated yet.
      </div>
    );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Generated SQL</span>
          {executionTime != null && (
            <span className="text-xs bg-purple-900/30 text-purple-400 border border-purple-800/40 px-2.5 py-0.5 rounded-full">
              ⚡ {executionTime}ms
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-purple-300 glass px-3 py-1.5 rounded-lg transition-all hover:border-purple-500/30"
        >
          {copied ? (
            <><span className="text-green-400">✓</span> Copied!</>
          ) : (
            <><svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Copy</>
          )}
        </button>
      </div>
      <pre
        className="glass rounded-xl p-5 overflow-x-auto font-mono text-sm leading-7 text-gray-300"
        dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }}
      />
    </div>
  );
}
