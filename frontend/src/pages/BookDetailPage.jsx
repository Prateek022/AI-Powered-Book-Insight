import { useEffect, useState } from "react";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { api } from "../lib/api";

export function BookDetailPage() {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDetail() {
      try {
        const [bookData, recommendationData] = await Promise.all([api.getBook(id), api.getRecommendations(id)]);
        setBook(bookData);
        setRecommendations(recommendationData.recommendations || []);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadDetail();
  }, [id]);

  if (error) {
    return <div className="glass-panel rounded-[28px] p-6 text-[var(--rose)]">{error}</div>;
  }

  if (!book) {
    return <div className="glass-panel rounded-[28px] p-6 text-[var(--fog)]">Loading book dossier...</div>;
  }

  return (
    <section className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
      <article className="glass-panel rounded-[32px] p-6">
        <Link to="/" className="mb-5 inline-flex items-center gap-2 text-sm text-[var(--fog)]">
          <ArrowLeft className="h-4 w-4" /> Back to dashboard
        </Link>
        <p className="text-xs uppercase tracking-[0.28em] text-[var(--gold)]">{book.category}</p>
        <h2 className="section-title mt-3 text-4xl">{book.title}</h2>
        <p className="mt-2 text-lg text-[var(--fog)]">by {book.author}</p>

        <div className="mt-6 grid gap-3 md:grid-cols-2">
          <div className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Summary</p>
            <p className="mt-3 text-sm leading-7">{book.summary}</p>
          </div>
          <div className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Recommendation Logic</p>
            <p className="mt-3 text-sm leading-7">{book.recommendation_pitch}</p>
          </div>
          <div className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Genre + Sentiment</p>
            <p className="mt-3 text-sm leading-7">{book.genre_prediction} · {book.sentiment_label}</p>
          </div>
          <div className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Highlighted Context</p>
            <p className="mt-3 text-sm leading-7">{book.highlight_quote}</p>
          </div>
        </div>

        <div className="mt-6 rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-[var(--fog)]">Description</p>
          <p className="mt-3 text-sm leading-7 text-[var(--fog)]">{book.description}</p>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {book.key_themes?.map((theme) => (
            <span key={theme} className="rounded-full bg-[rgba(240,187,120,0.1)] px-3 py-1 text-xs text-[var(--gold)]">
              {theme}
            </span>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <a className="rounded-full bg-[var(--gold)] px-4 py-2 text-sm text-[#1c130d]" href={book.book_url} target="_blank" rel="noreferrer">
            Open Source Page <ExternalLink className="ml-1 inline h-4 w-4" />
          </a>
          <Link className="rounded-full border border-[rgba(240,187,120,0.15)] px-4 py-2 text-sm text-[var(--fog)]" to={`/books/${book.id}/ask`}>
            Ask Questions About This Book
          </Link>
        </div>
      </article>

      <aside className="glass-panel rounded-[32px] p-6">
        <p className="text-xs uppercase tracking-[0.28em] text-[var(--gold)]">Related Reading</p>
        <h3 className="section-title mt-2 text-3xl">Why readers may also like</h3>
        <div className="mt-5 space-y-3">
          {recommendations.map((recommendation) => (
            <div key={recommendation.id} className="rounded-[24px] bg-[rgba(255,255,255,0.03)] p-4">
              <Link to={`/books/${recommendation.id}`} className="text-lg">{recommendation.title}</Link>
              <p className="mt-1 text-sm text-[var(--fog)]">{recommendation.author}</p>
              <p className="mt-3 text-sm leading-7 text-[var(--fog)]">{recommendation.why}</p>
            </div>
          ))}
        </div>
      </aside>
    </section>
  );
}
