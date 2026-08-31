import { Link } from "react-router-dom";
import { Button } from "../components/common/Button.jsx";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface-warm px-4 text-center">
      <div className="mb-4 text-5xl">🕉️</div>
      <h1 className="text-2xl font-bold tracking-tight text-text">Page not found</h1>
      <p className="mt-2 text-sm text-text-muted">The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-6">
        <Button variant="secondary">Back home</Button>
      </Link>
    </div>
  );
}
