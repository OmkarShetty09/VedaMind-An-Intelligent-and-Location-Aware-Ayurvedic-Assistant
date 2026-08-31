import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "../components/common/Button.jsx";
import { Input } from "../components/common/Input.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";

export function LoginPage() {
  const { signIn, error } = useAuthContext();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await signIn(form);
    setLoading(false);
    if (res.type?.endsWith("/fulfilled")) navigate("/chat");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-warm px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand text-xl text-white shadow-sm">
            🌿
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text">Welcome back</h1>
          <p className="mt-1 text-sm text-text-muted">Sign in to VedaMind.</p>
        </div>
        <div className="card p-6">
          <form className="space-y-4" onSubmit={submit}>
            <Input
              label="Email"
              type="email"
              required
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <Input
              label="Password"
              type="password"
              required
              placeholder="Enter your password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {error}
              </div>
            )}
            <Button type="submit" loading={loading} className="w-full">
              Sign in
            </Button>
          </form>
        </div>
        <p className="mt-5 text-center text-sm text-text-muted">
          New here?{" "}
          <Link to="/register" className="font-medium text-brand underline underline-offset-2 hover:text-brand-dark">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
