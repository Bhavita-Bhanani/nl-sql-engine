import { useState, useEffect, useCallback } from "react";
import api from "./api.js";
import QueryInput from "./components/QueryInput";
import ResultTable from "./components/ResultTable";
import SQLDisplay from "./components/SQLDisplay";
import QueryHistory from "./components/QueryHistory";
import SchemaViewer from "./components/SchemaViewer";

const TABS = ["Results", "SQL", "Explanation"];

export default function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("Results");
  const [schema, setSchema] = useState([]);
  const [schemaLoading, setSchemaLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [historyOpen, setHistoryOpen] = useState(true);

  const loadSchema = useCallback(async () => {
    setSchemaLoading(true);
    try {
      const res = await api.get("/schema");
      setSchema(res.data.tables || []);
    } catch { setSchema([]); }
    finally { setSchemaLoading(false); }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const res = await api.get("/history");
      setHistory(res.data || []);
    } catch { setHistory([]); }
  }, []);

  useEffect(() => { loadSchema(); loadHistory(); }, []);

  const handleSubmit = async () => {
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveTab("Results");
    try {
      const res = await api.post("/query", { question: question.trim() });
      setResult(res.data);
      if (!res.data.success) setError(res.data.error || "Query failed.");
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Something went wrong.");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ fontFamily: "'Inter', sans-serif" }}>

      {/* ── Navbar ─────────────────────────────────────────────────────── */}
      <header className="flex-shrink-0 border-b border-white/[0.06] px-6 py-3 flex items-center justify-between"
        style={{ background: "rgba(10,10,20,0.8)", backdropFilter: "blur(20px)" }}>
        <div className="flex items-center gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg,#7c3aed,#a855f7)" }}>
              <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <span className="font-bold text-white text-base gradient-text">NL-SQL Engine</span>
              <p className="text-xs text-gray-600 hidden sm:block leading-none mt-0.5">Ask your database in plain English</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Groq status */}
          <div className="flex items-center gap-2 glass px-3 py-1.5 rounded-full">
            <div className="glow-dot" />
            <span className="text-xs text-gray-400 font-medium">Groq · llama3</span>
          </div>
          <button
            onClick={() => setSidebarOpen(v => !v)}
            className="glass text-xs text-gray-400 hover:text-purple-300 px-3 py-1.5 rounded-xl transition-all hover:border-purple-500/30"
          >
            {sidebarOpen ? "Hide Schema" : "Show Schema"}
          </button>
        </div>
      </header>

      {/* ── Layout ─────────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-60 flex-shrink-0 border-r border-white/[0.05] overflow-y-auto"
            style={{ background: "rgba(10,10,20,0.6)", backdropFilter: "blur(10px)" }}>
            <div className="px-4 py-3 border-b border-white/[0.05]">
              <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Database Schema</h2>
            </div>
            <SchemaViewer schema={schema} loading={schemaLoading} />
          </aside>
        )}

        {/* Main */}
        <main className="flex-1 overflow-y-auto p-6 space-y-5">

          {/* Hero text (only before first query) */}
          {!result && !loading && (
            <div className="text-center py-6">
              <h1 className="text-3xl font-bold gradient-text mb-2">Ask Anything</h1>
              <p className="text-gray-600 text-sm">Type a question in plain English — AI converts it to SQL and runs it instantly</p>
            </div>
          )}

          {/* Query Input */}
          <QueryInput question={question} setQuestion={setQuestion} onSubmit={handleSubmit} loading={loading} />

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 rounded-2xl p-4 border border-red-900/40"
              style={{ background: "rgba(127,29,29,0.2)" }}>
              <span className="text-red-400 text-lg flex-shrink-0">⚠</span>
              <div>
                <p className="text-sm font-semibold text-red-300">Query Failed</p>
                <p className="text-sm text-red-400/80 mt-0.5 leading-relaxed">{error}</p>
              </div>
            </div>
          )}

          {/* Loading skeleton */}
          {loading && (
            <div className="glass rounded-2xl p-6 space-y-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="h-4 w-4 rounded-full bg-purple-900/60" />
                <div className="h-4 bg-white/[0.05] rounded-lg w-2/5" />
              </div>
              <div className="h-3 bg-white/[0.03] rounded-lg w-3/5" />
              <div className="h-40 bg-white/[0.03] rounded-xl mt-2" />
            </div>
          )}

          {/* Results card */}
          {result && (
            <div className="glass rounded-2xl overflow-hidden"
              style={{ boxShadow: "0 0 40px rgba(124,58,237,0.1)" }}>

              {/* Question header */}
              <div className="px-6 py-4 border-b border-white/[0.06] flex items-start justify-between gap-4"
                style={{ background: "rgba(139,92,246,0.06)" }}>
                <div>
                  <p className="text-xs text-gray-600 uppercase tracking-widest mb-1 font-semibold">Question</p>
                  <p className="text-sm text-gray-200 font-medium">{result.question}</p>
                </div>
                {result.success && (
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs glass border-emerald-800/40 text-emerald-400 px-3 py-1 rounded-full"
                      style={{ background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.25)" }}>
                      ✓ {result.result_count} rows
                    </span>
                    <span className="text-xs text-gray-600">⚡ {result.execution_time_ms}ms</span>
                  </div>
                )}
              </div>

              {/* Tabs */}
              <div className="flex border-b border-white/[0.06] px-6">
                {TABS.map((tab) => (
                  <button key={tab} onClick={() => setActiveTab(tab)}
                    className={`py-3 px-1 mr-6 text-sm font-semibold transition-all ${activeTab === tab ? "tab-active" : "tab-inactive"}`}>
                    {tab === "Results" && "📊 "}
                    {tab === "SQL" && "💾 "}
                    {tab === "Explanation" && "🤖 "}
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div className="p-6">
                {activeTab === "Results" && <ResultTable results={result.results} />}
                {activeTab === "SQL" && <SQLDisplay sql={result.sql} executionTime={result.execution_time_ms} />}
                {activeTab === "Explanation" && (
                  <div>
                    {result.explanation ? (
                      <div className="rounded-xl p-5" style={{ background: "rgba(139,92,246,0.08)", border: "1px solid rgba(139,92,246,0.2)" }}>
                        <div className="flex items-center gap-2 mb-3">
                          <div className="h-6 w-6 rounded-lg flex items-center justify-center text-sm"
                            style={{ background: "linear-gradient(135deg,#7c3aed,#a855f7)" }}>🤖</div>
                          <span className="text-xs font-bold text-purple-400 uppercase tracking-widest">AI Explanation</span>
                        </div>
                        <p className="text-gray-200 text-sm leading-relaxed">{result.explanation}</p>
                      </div>
                    ) : (
                      <p className="text-gray-600 text-sm text-center py-8">No explanation available.</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* History */}
          <div className="glass rounded-2xl overflow-hidden">
            <button
              onClick={() => setHistoryOpen(v => !v)}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-gray-500">🕐</span>
                <span className="text-sm font-semibold text-gray-300">Query History</span>
                {history.length > 0 && (
                  <span className="text-xs font-mono text-purple-400 glass px-2 py-0.5 rounded-full"
                    style={{ background: "rgba(139,92,246,0.15)" }}>
                    {history.length}
                  </span>
                )}
              </div>
              <span className="text-gray-600 text-xs">{historyOpen ? "▾" : "▸"}</span>
            </button>
            {historyOpen && (
              <div className="px-4 pb-4 border-t border-white/[0.04]">
                <div className="pt-3">
                  <QueryHistory history={history} onRerun={setQuestion} onRefresh={loadHistory} />
                </div>
              </div>
            )}
          </div>

        </main>
      </div>
    </div>
  );
}
