import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "../components/common/Button.jsx";
import { Input } from "../components/common/Input.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";

export function RegisterPage() {
  const { signUp, error } = useAuthContext();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "", display_name: "" });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await signUp(form);
    setLoading(false);
    if (res.type?.endsWith("/fulfilled")) navigate("/");
  };

  return (
    <div className="mx-auto max-w-sm py-12">
      <h1 className="text-2xl font-semibold text-text">Create your account</h1>
      <p className="mt-1 text-sm text-text-muted">Free. No card. Unsubscribe anytime.</p>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <Input
          label="Email"
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <Input
          label="Display name"
          value={form.display_name}
          onChange={(e) => setForm({ ...form, display_name: e.target.value })}
        />
        <Input
          label="Password"
          type="password"
          required
          minLength={8}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" loading={loading} className="w-full">
          Create account
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-text-muted">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
