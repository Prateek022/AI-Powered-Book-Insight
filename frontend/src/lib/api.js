const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || "Request failed.");
  }
  return payload;
}

export const api = {
  getOverview: () => request("/overview/"),
  listBooks: () => request("/books/"),
  getBook: (id) => request(`/books/${id}/`),
  getRecommendations: (id) => request(`/books/${id}/recommendations/`),
  getQueryHistory: (id) => request(`/books/${id}/queries/`),
  askQuestion: (id, question) =>
    request(`/books/${id}/ask/`, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  scrapeBooks: (payload) =>
    request("/books/upload/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
