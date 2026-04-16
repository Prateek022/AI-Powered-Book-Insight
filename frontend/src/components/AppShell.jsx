import { BookOpenText, Sparkles } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export function AppShell() {
  return (
    <div className="min-h-screen px-4 py-5 text-[var(--ink)] md:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-4">
        <header className="glass-panel flex flex-col gap-4 rounded-[28px] px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.35em] text-[var(--gold)]">
              <Sparkles className="h-4 w-4" />
              Document Intelligence Platform
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-2xl border border-[rgba(240,187,120,0.25)] bg-[rgba(240,187,120,0.08)] p-3">
                <BookOpenText className="h-6 w-6 text-[var(--gold)]" />
              </div>
              <div>
                <h1 className="section-title text-3xl font-semibold md:text-4xl">Libriscope Atlas</h1>
                <p className="mt-1 max-w-2xl text-sm text-[var(--fog)]">
                  Scrape, enrich, retrieve, and interrogate books with source-grounded answers and reviewer-friendly insight cards.
                </p>
              </div>
            </div>
          </div>

          <nav className="flex flex-wrap gap-2 text-sm">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `rounded-full px-4 py-2 transition ${isActive ? "bg-[var(--gold)] text-[#1c130d]" : "border border-[rgba(240,187,120,0.15)] bg-[rgba(255,255,255,0.03)] text-[var(--fog)]"}`
              }
            >
              Dashboard
            </NavLink>
          </nav>
        </header>

        <Outlet />
      </div>
    </div>
  );
}
