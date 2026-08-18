import { Link } from "react-router-dom";
import { Button } from "../components/common/Button.jsx";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <p className="text-6xl">🕉️</p>
      <h1 className="text-2xl font-semibold text-text">Page not found</h1>
      <Link to="/">
        <Button variant="secondary">Back home</Button>
      </Link>
    </div>
  );
}
