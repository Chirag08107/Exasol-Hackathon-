import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    login(form);
    navigate("/");
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <p className="auth-visual-quote">
          Pick up right where you left off.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Welcome back</div>
          <h2 className="mb-4">Login</h2>
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-2">
            <input className="input-brand" type="email" name="email" placeholder="Email" onChange={handleChange} required />
            <input className="input-brand" type="password" name="password" placeholder="Password" onChange={handleChange} required />
            <button className="btn-brand mt-2">Login</button>
          </form>
          <div className="mt-3">
            No account? <Link to="/signup">Sign Up</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
