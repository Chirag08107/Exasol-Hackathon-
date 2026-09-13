import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Verify() {
  const [form, setForm] = useState({ phone: "", address: "", aadhaarNumber: "", otp: "" });
  const [otpSent, setOtpSent] = useState(false);
  const [phoneVerified, setPhoneVerified] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);
  const [otpExpiryTimer, setOtpExpiryTimer] = useState(0);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ type: "", message: "" });

  const navigate = useNavigate();
  const { sendOtp, resendOtp, verifyOtp, verify } = useAuth();

  useEffect(() => {
    if (resendTimer <= 0 && otpExpiryTimer <= 0) return;
    const timer = setInterval(() => {
      setResendTimer((t) => (t > 0 ? t - 1 : 0));
      setOtpExpiryTimer((t) => (t > 0 ? t - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendTimer, otpExpiryTimer]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remaining = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`;
  };

  const getFullPhoneNumber = () => `+91${form.phone}`;

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, "");
    setForm((f) => ({ ...f, phone: value.slice(0, 10) }));
    setPhoneVerified(false);
    setOtpSent(false);
  };

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSendOtp = async () => {
    if (form.phone.length !== 10) {
      setAlert({ type: "error", message: "Please enter a valid 10-digit phone number." });
      return;
    }
    setLoading(true);
    setAlert({ type: "", message: "" });
    try {
      await sendOtp(getFullPhoneNumber());
      setOtpSent(true);
      setPhoneVerified(false);
      setForm((f) => ({ ...f, otp: "" }));
      setResendTimer(60);
      setOtpExpiryTimer(300);
      setAlert({ type: "success", message: "OTP sent successfully! Please check your phone." });
    } catch (error) {
      setAlert({ type: "error", message: error.message || "Failed to send OTP." });
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (resendTimer > 0) return;
    setLoading(true);
    try {
      await resendOtp(getFullPhoneNumber());
      setForm((f) => ({ ...f, otp: "" }));
      setResendTimer(60);
      setOtpExpiryTimer(300);
      setAlert({ type: "success", message: "OTP resent successfully!" });
    } catch (error) {
      setAlert({ type: "error", message: error.message || "Failed to resend OTP." });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!form.otp.trim()) {
      setAlert({ type: "error", message: "Please enter the OTP." });
      return;
    }
    if (otpExpiryTimer <= 0) {
      setAlert({ type: "error", message: "OTP has expired. Please resend the OTP." });
      return;
    }
    setLoading(true);
    try {
      await verifyOtp(getFullPhoneNumber(), form.otp);
      setPhoneVerified(true);
      setAlert({ type: "success", message: "Phone number verified successfully!" });
    } catch (error) {
      setAlert({ type: "error", message: error.message || "Invalid OTP. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!phoneVerified) {
      setAlert({ type: "error", message: "Please verify your phone number first." });
      return;
    }
    if (!form.address.trim()) {
      setAlert({ type: "error", message: "Please enter your address." });
      return;
    }
    if (form.aadhaarNumber.length !== 12) {
      setAlert({ type: "error", message: "Please enter a valid 12-digit Aadhaar number." });
      return;
    }
    setLoading(true);
    try {
      await verify({
        phone: getFullPhoneNumber(),
        otp: form.otp,
        address: form.address,
        aadhaarNumber: form.aadhaarNumber,
      });
      setAlert({ type: "success", message: "Verification completed successfully!" });
      setTimeout(() => navigate("/"), 1200);
    } catch (error) {
      setAlert({ type: "error", message: error.message || "Verification failed." });
    } finally {
      setLoading(false);
    }
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
            <div className={`step-dot ${phoneVerified ? "done" : ""}`} />
          </div>

          {alert.message && (
            <div className={`alert ${alert.type === "success" ? "alert-success" : "alert-danger"}`}>
              {alert.type === "success" ? "✓ " : "⚠ "}{alert.message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="d-flex flex-column gap-3">
            <div className="field-group">
              <label className="field-label">Phone number</label>
              <div className="d-flex gap-2 align-items-center">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "0 0.85rem",
                    height: "44px",
                    border: "1px solid var(--line)",
                    borderRadius: "var(--radius)",
                    background: "var(--bg)",
                    fontWeight: 500,
                    color: "var(--ink-soft)",
                  }}
                >
                  +91
                </div>
                <input
                  className="input-brand flex-grow-1"
                  name="phone"
                  type="tel"
                  inputMode="numeric"
                  placeholder="10-digit mobile number"
                  value={form.phone}
                  onChange={handlePhoneChange}
                  disabled={phoneVerified || loading}
                  maxLength={10}
                  required
                  style={phoneVerified ? { borderColor: "var(--accent)" } : undefined}
                />
                {!otpSent && !phoneVerified && (
                  <button type="button" className="btn-brand-outline" onClick={handleSendOtp} disabled={loading} style={{ whiteSpace: "nowrap" }}>
                    {loading ? "Sending…" : "Send OTP"}
                  </button>
                )}
                {phoneVerified && <span style={{ color: "var(--accent)", fontSize: "1.3rem", fontWeight: 700 }}>✓</span>}
              </div>
            </div>

            {otpSent && !phoneVerified && (
              <div className="field-group">
                <label className="field-label">Enter OTP</label>
                <input
                  className="input-brand w-100"
                  name="otp"
                  type="text"
                  inputMode="numeric"
                  placeholder="6-digit code"
                  value={form.otp}
                  onChange={(e) => setForm((f) => ({ ...f, otp: e.target.value.replace(/\D/g, "").slice(0, 6) }))}
                  maxLength={6}
                  disabled={loading}
                  required
                />
                <div style={{ fontSize: "0.78rem", color: "var(--ink-soft)", marginTop: "0.35rem" }}>
                  {otpExpiryTimer > 0 ? (
                    <>OTP expires in <strong>{formatTime(otpExpiryTimer)}</strong></>
                  ) : (
                    <span style={{ color: "var(--warn)" }}>OTP has expired.</span>
                  )}
                </div>
                <div className="d-flex justify-content-between align-items-center mt-2">
                  {resendTimer > 0 ? (
                    <span style={{ fontSize: "0.82rem", color: "var(--ink-soft)" }}>
                      Resend OTP in <strong>{formatTime(resendTimer)}</strong>
                    </span>
                  ) : (
                    <button type="button" className="btn-ghost p-0" onClick={handleResendOtp} disabled={loading} style={{ fontSize: "0.85rem" }}>
                      Resend OTP
                    </button>
                  )}
                  <button type="button" className="btn-brand-outline" onClick={handleVerifyOtp} disabled={loading}>
                    {loading ? "Verifying…" : "Verify OTP"}
                  </button>
                </div>
              </div>
            )}

            <div className="field-group">
              <label className="field-label">Address</label>
              <input className="input-brand w-100" name="address" placeholder="Current residential address" value={form.address} onChange={handleChange} disabled={loading} required />
            </div>
            <div className="field-group">
              <label className="field-label">Aadhaar number</label>
              <input
                className="input-brand w-100"
                name="aadhaarNumber"
                inputMode="numeric"
                placeholder="XXXXXXXXXXXX"
                value={form.aadhaarNumber}
                onChange={(e) => setForm((f) => ({ ...f, aadhaarNumber: e.target.value.replace(/\D/g, "").slice(0, 12) }))}
                maxLength={12}
                disabled={loading}
                required
              />
            </div>
            <button className="btn-warn mt-1" disabled={!phoneVerified || loading} style={{ opacity: phoneVerified && !loading ? 1 : 0.6 }}>
              {loading ? "Verifying…" : "Verify"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
