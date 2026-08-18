import { Link } from "react-router-dom";
import { Button } from "../components/common/Button.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";

export function HomePage() {
  const { isAuthenticated } = useAuthContext();
  return (
    <div className="flex flex-col items-center gap-6 py-10 text-center">
      <div className="text-5xl">🌿</div>
      <h1 className="max-w-xl text-3xl font-semibold leading-tight text-text">
        Evidence-grounded, location-aware Ayurvedic guidance
      </h1>
      <p className="max-w-lg text-sm leading-relaxed text-text-muted">
        Ask about herbs, routines, and seasons. VedaMind answers only from classical Ayurvedic sources, checks every
        answer for safety, and tunes daily routines to your local time and weather.
      </p>
      <div className="flex gap-3">
        <Link to="/chat">
          <Button>Ask VedaMind</Button>
        </Link>
        <Link to="/dinacharya">
          <Button variant="secondary">See my routine</Button>
        </Link>
      </div>
      {!isAuthenticated && (
        <Link to="/register" className="text-sm font-medium text-brand underline">
          Create a free account
        </Link>
      )}
    </div>
  );
}
