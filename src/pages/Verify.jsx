import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Verify() {
  const [form, setForm] = useState({ phone: "", address: "", aadhaarNumber: "", otp: "" });
  const navigate = useNavigate();
  const { verify } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    verify(form);
    navigate("/");
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <p className="auth-visual-quote">
          One last step — this keeps your account and everyone else's secure.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Almost there</div>
          <h2 className="mb-4">Verify Yourself</h2>
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-2">
            <input className="input-brand" name="phone" placeholder="Phone (OTP will be sent)" onChange={handleChange} required />
            <input className="input-brand" name="otp" placeholder="Enter OTP" onChange={handleChange} required />
            <input className="input-brand" name="address" placeholder="Address" onChange={handleChange} required />
            <input className="input-brand" name="aadhaarNumber" placeholder="Aadhaar Card Number" onChange={handleChange} required />
            <button className="btn-warn mt-2">Verify</button>
          </form>
        </div>
      </div>
    </div>
  );
}
