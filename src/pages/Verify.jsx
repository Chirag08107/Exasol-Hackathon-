import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Verify() {
  const [form, setForm] = useState({ phone: "", address: "", aadhaarNumber: "", otp: "" });
  const [otpSent, setOtpSent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { verify } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSendOtp = () => {
    if (!form.phone) return;
    setOtpSent(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitting(true);
    verify(form);
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
          One last step — this keeps your account and everyone else's secure.
        </p>
        <p className="auth-visual-foot">
          Your details are only used to verify identity and are never shared without consent.
        </p>
      </div>
      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">Almost there</div>
          <h2 className="mb-3">Verify Yourself</h2>

          <div className="step-track">
            <div className="step-dot done" />
            <div className="step-dot done" />
            <div className="step-dot" />
          </div>

          <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
            <div className="field-group">
              <label className="field-label">Phone number</label>
              <div className="d-flex gap-2">
                <input
                  className="input-brand flex-grow-1"
                  name="phone"
                  placeholder="10-digit mobile number"
                  value={form.phone}
                  onChange={handleChange}
                  required
                />
                <button type="button" className="btn-brand-outline" onClick={handleSendOtp} style={{ whiteSpace: "nowrap" }}>
                  {otpSent ? "Resend OTP" : "Send OTP"}
                </button>
              </div>
              {otpSent && (
                <div style={{ fontSize: "0.78rem", color: "var(--accent-hover)", marginTop: "0.35rem" }}>
                  OTP sent (mock) — enter any 6 digits below.
                </div>
              )}
            </div>
            <div className="field-group">
              <label className="field-label">Enter OTP</label>
              <input className="input-brand w-100" name="otp" placeholder="6-digit code" value={form.otp} onChange={handleChange} required />
            </div>
            <div className="field-group">
              <label className="field-label">Address</label>
              <input className="input-brand w-100" name="address" placeholder="Current residential address" value={form.address} onChange={handleChange} required />
            </div>
            <div className="field-group">
              <label className="field-label">Aadhaar number</label>
              <input className="input-brand w-100" name="aadhaarNumber" placeholder="XXXX XXXX XXXX" value={form.aadhaarNumber} onChange={handleChange} required />
            </div>
            <button className="btn-warn mt-1" disabled={submitting}>
              {submitting ? "Verifying…" : "Verify"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
