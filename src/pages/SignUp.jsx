import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import GoogleSignIn from "../components/GoogleSignIn";

export default function SignUp() {
  const [form, setForm] = useState({
    firstName: "", middleName: "", lastName: "",
    userName: "", email: "", password: "",
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { signup, login } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await signup(form);
      // Registration alone doesn't return a session token, so log in
      // right after with the same credentials to get one.
      await login({ email: form.email, password: form.password });
      navigate("/verify");
    } catch (err) {
      setError(err.message || "Unable to create account");
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <p className="auth-visual-quote">
          Get set up in a couple of minutes, verify once, and you're in.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Create an account</div>
          <h2 className="mb-4">Sign Up</h2>
          {error && <div className="text-danger small mb-2">{error}</div>}
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-2">
            <input className="input-brand" name="firstName" placeholder="First Name" onChange={handleChange} required />
            <input className="input-brand" name="middleName" placeholder="Middle Name" onChange={handleChange} />
            <input className="input-brand" name="lastName" placeholder="Last Name" onChange={handleChange} required />
            <input className="input-brand" name="userName" placeholder="Username" onChange={handleChange} required />
            <input className="input-brand" type="email" name="email" placeholder="Email / Gmail" onChange={handleChange} required />
            <input className="input-brand" type="password" name="password" placeholder="Password" onChange={handleChange} required />
            <button className="btn-brand mt-2">Submit</button>
          </form>
          <div className="my-2 text-center text-muted">or</div>
          <GoogleSignIn text="signup_with" />
          <div className="mt-3">
            Already have an account? <Link to="/login">Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
