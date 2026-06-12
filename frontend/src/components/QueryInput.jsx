import { useRef } from "react";

const EXAMPLE_QUESTIONS = [
  "Top 5 customers by total spending",
  "Products with low stock (< 20)",
  "Average order value by country",
  "Monthly sales for last 6 months",
  "Most revenue by product category",
  "All gold tier customers",
  "Average product rating per category",
  "How many orders were cancelled?",
];

export default function QueryInput({ question, setQuestion, onSubmit, loading }) {
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (!loading && question.trim()) onSubmit();
    }
  };

  return (
    <div className="space-y-4">
      {/* Input box */}
      <div className="relative glass rounded-2xl overflow-hidden transition-all focus-within:border-purple-500/50 focus-within:shadow-[0_0_30px_rgba(124,58,237,0.2)]">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask your database anything in plain English…"
          rows={3}
          className="w-full bg-transparent px-5 py-4 pr-36 text-gray-100 placeholder-gray-600 resize-none focus:outline-none text-sm leading-relaxed"
        />
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <span className="text-xs text-gray-700 hidden sm:block">Ctrl+Enter</span>
          <button
            onClick={onSubmit}
            disabled={loading || !question.trim()}
            className="btn-primary flex items-center gap-2 text-white px-4 py-2 rounded-xl text-sm font-semibold disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Thinking…
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Ask AI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Example chips */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-600 self-center mr-1">Try:</span>
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => { setQuestion(q); textareaRef.current?.focus(); }}
            className="chip text-xs px-3 py-1.5 rounded-full font-medium"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
