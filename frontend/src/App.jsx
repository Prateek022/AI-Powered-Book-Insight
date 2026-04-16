import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { AskPage } from "./pages/AskPage";
import { BookDetailPage } from "./pages/BookDetailPage";
import { DashboardPage } from "./pages/DashboardPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/books/:id" element={<BookDetailPage />} />
          <Route path="/books/:id/ask" element={<AskPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
