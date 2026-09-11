import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitting(true);
    login(form);
    navigate("/");
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <div className="auth-visual-logo">
          <span className="nav-logo-mark">FS</span>
          <span className="font-display" style={{ fontSize: "1.15rem", color: "#fff" }}>FormSahay</span>
        </div>
        <p className="auth-visual-quote">
          Pick up right where you left off.
        </p>
        <p className="auth-visual-foot">
          Trusted guidance across 80+ Indian government forms — PAN, Aadhaar, passport, ITR, and more.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Welcome back</div>
          <h2 className="mb-4">Login</h2>
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
            <div className="field-group">
              <label className="field-label">Email</label>
              <input
                className="input-brand w-100"
                type="email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="field-group">
              <label className="field-label">Password</label>
              <input
                className="input-brand w-100"
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                required
                style={{ paddingRight: "3.2rem" }}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((s) => !s)}
                style={{ top: "2.15rem" }}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
            <div className="d-flex justify-content-end">
              <Link to="/login" className="nav-link-quiet" style={{ fontSize: "0.85rem" }}>Forgot password?</Link>
            </div>
            <button className="btn-brand mt-1" disabled={submitting}>
              {submitting ? "Logging in…" : "Login"}
            </button>
          </form>
          <div className="mt-4 text-center" style={{ color: "var(--ink-soft)", fontSize: "0.92rem" }}>
            No account? <Link to="/signup">Sign Up</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
