import { useEffect, useState } from "react";
import { ArrowLeft, Bot, Quote } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { api } from "../lib/api";

const sampleQuestions = [
  "What is the central conflict of this book?",
  "What kind of reader would enjoy this title?",
  "Summarize the tone and themes with citations.",
];

export function AskPage() {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [question, setQuestion] = useState(sampleQuestions[0]);
  const [answer, setAnswer] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getBook(id), api.getQueryHistory(id)])
      .then(([bookData, historyData]) => {
        setBook(bookData);
        setHistory(historyData.history || []);
      })
      .catch((loadError) => setError(loadError.message));
  }, [id]);

  async function askCurrentQuestion(nextQuestion = question) {
    setLoading(true);
    setError("");
    try {
      const response = await api.askQuestion(id, nextQuestion);
      setAnswer(response);
      const historyData = await api.getQueryHistory(id);
      setHistory(historyData.history || []);
    } catch (askError) {
      setError(askError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
      <aside className="glass-panel rounded-[32px] p-6">
        <Link to={book ? `/books/${book.id}` : "/"} className="inline-flex items-center gap-2 text-sm text-[var(--fog)]">
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>
        <p className="mt-5 text-xs uppercase tracking-[0.28em] text-[var(--gold)]">Contextual Q&A</p>
        <h2 className="section-title mt-2 text-3xl">{book ? `Ask ${book.title}` : "Load book context..."}</h2>
        <p className="mt-3 text-sm leading-7 text-[var(--fog)]">
          The answer engine retrieves the most relevant chunks from Chroma, assembles context, and returns a grounded answer with citations.
        </p>

        <div className="mt-6 rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
          <label className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Question</label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="mt-3 min-h-36 w-full rounded-[20px] border border-[rgba(240,187,120,0.14)] bg-[rgba(18,12,8,0.55)] p-4 text-sm outline-none"
          />
          <button
            onClick={() => askCurrentQuestion()}
            disabled={loading}
            className="mt-4 rounded-full bg-[var(--gold)] px-4 py-2 text-sm text-[#1c130d] disabled:opacity-70"
          >
            {loading ? "Thinking..." : "Ask with Retrieval"}
          </button>
        </div>

        <div className="mt-6 space-y-2">
          {sampleQuestions.map((sample) => (
            <button
              key={sample}
              onClick={() => {
                setQuestion(sample);
                askCurrentQuestion(sample);
              }}
              className="block w-full rounded-[18px] border border-[rgba(240,187,120,0.14)] px-4 py-3 text-left text-sm text-[var(--fog)]"
            >
              {sample}
            </button>
          ))}
        </div>
      </aside>

      <article className="glass-panel rounded-[32px] p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-[rgba(132,216,196,0.1)] p-3 text-[var(--mint)]">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">RAG Response</p>
            <h3 className="text-2xl">Answer with evidence windows</h3>
          </div>
        </div>

        {error ? <p className="mt-4 rounded-2xl bg-[rgba(240,138,118,0.12)] px-4 py-3 text-sm text-[var(--rose)]">{error}</p> : null}

        {answer ? (
          <div className="mt-6 space-y-5">
            <div className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-5">
              <p className="text-sm leading-7">{answer.answer}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--fog)]">
                <span className="rounded-full bg-[rgba(132,216,196,0.1)] px-3 py-1 text-[var(--mint)]">
                  {answer.cache_hit ? "Cache hit" : "Fresh retrieval"}
                </span>
                <span className="rounded-full bg-[rgba(240,187,120,0.1)] px-3 py-1 text-[var(--gold)]">
                  {answer.latency_ms} ms
                </span>
              </div>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Citations</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {answer.citations.map((citation) => (
                  <span key={`${citation.label}-${citation.chunk}`} className="rounded-full border border-[rgba(240,187,120,0.14)] px-3 py-2 text-xs text-[var(--fog)]">
                    {citation.label}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Retrieved Context Windows</p>
              <div className="mt-3 space-y-3">
                {answer.context_windows.map((window, index) => (
                  <div key={index} className="rounded-[22px] bg-[rgba(255,255,255,0.03)] p-4 text-sm leading-7 text-[var(--fog)]">
                    <Quote className="mb-3 h-4 w-4 text-[var(--gold)]" />
                    {window}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 rounded-[24px] bg-[rgba(255,255,255,0.03)] p-6 text-sm leading-7 text-[var(--fog)]">
            Ask a question to see retrieved context, citations, cache behavior, and a grounded answer.
          </div>
        )}

        {history.length ? (
          <div className="mt-6">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Recent query history</p>
            <div className="mt-3 space-y-3">
              {history.slice(0, 4).map((entry) => (
                <div key={entry.id} className="rounded-[20px] bg-[rgba(255,255,255,0.03)] p-4">
                  <p className="text-sm text-[var(--ink)]">{entry.question}</p>
                  <p className="mt-2 text-sm leading-7 text-[var(--fog)]">{entry.answer}</p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </article>
    </section>
  );
}
