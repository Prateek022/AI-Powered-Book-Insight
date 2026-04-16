import { ArrowRight, Brain, Star } from "lucide-react";
import { Link } from "react-router-dom";

export function BookCard({ book }) {
  return (
    <article className="glass-panel group rounded-[26px] p-5 transition duration-200 hover:-translate-y-1">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-[var(--gold)]">{book.category || "Books"}</p>
          <h3 className="mt-2 text-2xl leading-tight">{book.title}</h3>
          <p className="mt-1 text-sm text-[var(--fog)]">by {book.author}</p>
        </div>
        <div className="rounded-full border border-[rgba(240,187,120,0.18)] px-3 py-2 text-sm text-[var(--gold)]">
          {book.genre_prediction}
        </div>
      </div>

      <p className="line-clamp-4 text-sm leading-6 text-[var(--fog)]">{book.summary || book.description}</p>

      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-[rgba(132,216,196,0.1)] px-3 py-1 text-[var(--mint)]">{book.sentiment_label}</span>
        {book.key_themes?.slice(0, 2).map((theme) => (
          <span key={theme} className="rounded-full bg-[rgba(240,187,120,0.1)] px-3 py-1 text-[var(--gold)]">
            {theme}
          </span>
        ))}
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-[rgba(240,187,120,0.1)] pt-4">
        <div className="flex items-center gap-4 text-sm text-[var(--fog)]">
          <span className="flex items-center gap-1"><Star className="h-4 w-4 text-[var(--gold)]" /> {book.rating}</span>
          <span className="flex items-center gap-1"><Brain className="h-4 w-4 text-[var(--mint)]" /> {book.review_count} reviews</span>
        </div>
        <div className="flex gap-2">
          <Link className="rounded-full border border-[rgba(240,187,120,0.15)] px-4 py-2 text-sm text-[var(--fog)]" to={`/books/${book.id}`}>
            Details
          </Link>
          <Link className="rounded-full bg-[var(--gold)] px-4 py-2 text-sm text-[#1c130d]" to={`/books/${book.id}/ask`}>
            Ask <ArrowRight className="ml-1 inline h-4 w-4" />
          </Link>
        </div>
      </div>
    </article>
  );
}
