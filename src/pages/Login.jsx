import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import GoogleSignIn from "../components/GoogleSignIn";

export default function Login() {
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await login(form);
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed");
    }
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

          <div className="eyebrow">
            Welcome back
          </div>

          <h2 className="mb-4">
            Login
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="d-flex flex-column gap-2"
          >
            <input
              className="input-brand"
              type="email"
              name="email"
              placeholder="Email"
              value={form.email}
              onChange={handleChange}
              required
            />

            <input
              className="input-brand"
              type="password"
              name="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
            />

            <button
              type="submit"
              className="btn-brand mt-2"
            >
              Login
            </button>

            {/* GOOGLE LOGIN */}
            <div className="my-2 text-center text-muted">
              or
            </div>

            <GoogleSignIn text="signin_with" />
          </form>

          <div className="mt-3">
            No account?{" "}
            <Link to="/signup">
              Sign Up
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}