import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useSelector } from "react-redux";

import { Button } from "../components/common/Button.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { store } from "../store/index.js";
import { loadProfile } from "../store/doshaSlice.js";

function DoshaProfileCard() {
  const { profile } = useSelector((s) => s.dosha);

  useEffect(() => {
    store.dispatch(loadProfile());
  }, []);

  if (!profile || !profile.dominant_dosha) {
    return (
      <Link to="/dosha" className="card-hover block p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Dosha Profile</p>
            <p className="mt-2 text-sm text-text-muted">Not yet assessed</p>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-lg">
            🧘
          </div>
        </div>
        <div className="mt-4 flex items-center gap-1 text-sm font-medium text-brand">
          Complete assessment
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </div>
      </Link>
    );
  }

  const dosha = profile.dominant_dosha.charAt(0).toUpperCase() + profile.dominant_dosha.slice(1);
  const colors = { Vata: "text-teal-600", Pitta: "text-amber-600", Kapha: "text-emerald-600" };

  return (
    <Link to="/dosha" className="card-hover block p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Dosha Profile</p>
          <p className={`mt-2 text-xl font-bold ${colors[dosha] || "text-brand"}`}>{dosha}</p>
          {profile.secondary_dosha && (
            <p className="mt-0.5 text-xs text-text-muted">
              Secondary: {profile.secondary_dosha.charAt(0).toUpperCase() + profile.secondary_dosha.slice(1)}
            </p>
          )}
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-lg">
          🧘
        </div>
      </div>
      <div className="mt-4 flex items-center gap-1 text-sm font-medium text-brand">
        View details
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      </div>
    </Link>
  );
}

function DinacharyaCard() {
  return (
    <Link to="/dinacharya" className="card-hover block p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Daily Routine</p>
          <p className="mt-2 text-sm text-text-muted">Tuned to your time, season & weather</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-lg">
          🕐
        </div>
      </div>
      <div className="mt-4 flex items-center gap-1 text-sm font-medium text-brand">
        View routine
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      </div>
    </Link>
  );
}

function SeasonalCard() {
  const now = new Date();
  const month = now.getMonth();
  let season, emoji;
  if (month >= 2 && month <= 4) { season = "Vasant (Spring)"; emoji = "🌸"; }
  else if (month >= 5 && month <= 6) { season = "Grishma (Summer)"; emoji = "☀️"; }
  else if (month >= 7 && month <= 8) { season = "Varsha (Monsoon)"; emoji = "🌧️"; }
  else if (month >= 9 && month <= 10) { season = "Sharad (Autumn)"; emoji = "🍂"; }
  else if (month === 11 || month === 0) { season = "Hemant (Early Winter)"; emoji = "🍁"; }
  else { season = "Shishir (Late Winter)"; emoji = "❄️"; }

  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Current Season</p>
          <p className="mt-2 text-sm font-medium text-text">{emoji} {season}</p>
          <p className="mt-1 text-xs text-text-muted">Ayurvedic ritu guidance</p>
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-lg">
          {emoji}
        </div>
      </div>
    </div>
  );
}

export function HomePage() {
  const { isAuthenticated } = useAuthContext();

  return (
    <div className="space-y-10 py-4">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-50 via-surface to-brand-100/50 px-6 py-12 text-center sm:px-10 sm:py-16">
        <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-brand/5" />
        <div className="pointer-events-none absolute -bottom-12 -left-12 h-48 w-48 rounded-full bg-brand/5" />

        <div className="relative">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/80 text-2xl shadow-soft backdrop-blur-sm">
            🌿
          </div>
          <h1 className="mx-auto max-w-lg text-3xl font-bold leading-tight tracking-tight text-text sm:text-4xl">
            Evidence-grounded Ayurvedic guidance, personalized for you
          </h1>
          <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-text-muted">
            Explore herbs, daily routines, seasonal living, and classical Ayurvedic knowledge grounded in traditional sources.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/chat">
              <Button className="px-6 py-3 text-sm">Ask VedaMind</Button>
            </Link>
            <Link to="/dinacharya">
              <Button variant="secondary" className="px-6 py-3 text-sm">View my routine</Button>
            </Link>
          </div>
          {!isAuthenticated && (
            <p className="mt-6 text-sm text-text-muted">
              New to VedaMind?{" "}
              <Link to="/register" className="font-medium text-brand underline underline-offset-2 hover:text-brand-dark">
                Create a free account
              </Link>
            </p>
          )}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <DoshaProfileCard />
        <DinacharyaCard />
        <SeasonalCard />
      </section>
    </div>
  );
}
