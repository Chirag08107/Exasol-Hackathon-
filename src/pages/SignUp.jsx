import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function SignUp() {
  const [form, setForm] = useState({
    firstName: "", middleName: "", lastName: "",
    userName: "", email: "", password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { signup } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitting(true);
    signup(form);
    navigate("/verify");
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <div className="auth-visual-logo">
          <span className="nav-logo-mark">FS</span>
          <span className="font-display" style={{ fontSize: "1.15rem", color: "#fff" }}>FormSahay</span>
        </div>
        <p className="auth-visual-quote">
          Get set up in a couple of minutes, verify once, and you're in.
        </p>
        <p className="auth-visual-foot">
          One account handles PAN, Aadhaar, passport, ITR, and 76 more forms.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Create an account</div>
          <h2 className="mb-4">Sign Up</h2>
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
            <div className="d-flex gap-2">
              <div className="field-group flex-grow-1">
                <label className="field-label">First name</label>
                <input className="input-brand w-100" name="firstName" placeholder="First name" onChange={handleChange} required />
              </div>
              <div className="field-group flex-grow-1">
                <label className="field-label">Last name</label>
                <input className="input-brand w-100" name="lastName" placeholder="Last name" onChange={handleChange} required />
              </div>
            </div>
            <div className="field-group">
              <label className="field-label">Middle name <span style={{ color: "#8FA09B" }}>(optional)</span></label>
              <input className="input-brand w-100" name="middleName" placeholder="Middle name" onChange={handleChange} />
            </div>
            <div className="field-group">
              <label className="field-label">Username</label>
              <input className="input-brand w-100" name="userName" placeholder="Choose a username" onChange={handleChange} required />
            </div>
            <div className="field-group">
              <label className="field-label">Email</label>
              <input className="input-brand w-100" type="email" name="email" placeholder="you@example.com" onChange={handleChange} required />
            </div>
            <div className="field-group">
              <label className="field-label">Password</label>
              <input
                className="input-brand w-100"
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="At least 8 characters"
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
            <button className="btn-brand mt-1" disabled={submitting}>
              {submitting ? "Creating account…" : "Create account"}
            </button>
            <div className="divider-text">or</div>
            <button type="button" className="btn-brand-outline">Sign in with Google</button>
          </form>
          <div className="mt-4 text-center" style={{ color: "var(--ink-soft)", fontSize: "0.92rem" }}>
            Already have an account? <Link to="/login">Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
