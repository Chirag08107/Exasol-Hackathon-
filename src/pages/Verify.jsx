import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Verify() {
  const [form, setForm] = useState({ phone: "", address: "", aadhaarNumber: "", otp: "" });
  const [otpSent, setOtpSent] = useState(false);
  const [phoneVerified, setPhoneVerified] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { sendOtp, verifyOtp, verify } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const fullPhone = () => `+91${form.phone}`;

  // The real backend requires the phone number to be OTP-verified
  // before /verify will accept the form (see backend/services/
  // auth_service.py: complete_user_verification). The original
  // skeleton had no OTP step at all, so it's added here — everything
  // else is unchanged from the original layout.
  const handleSendOtp = async () => {
    setError("");

    if (!form.phone.trim()) {
      setError("Enter a phone number first");
      return;
    }

    try {
      await sendOtp(fullPhone());
      setOtpSent(true);
    } catch (err) {
      setError(err.message || "Failed to send OTP");
    }
  };

  const handleVerifyOtp = async () => {
    setError("");

    try {
      await verifyOtp(fullPhone(), form.otp);
      setPhoneVerified(true);
    } catch (err) {
      setError(err.message || "Failed to verify OTP");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!phoneVerified) {
      setError("Please verify your phone number first");
      return;
    }

    try {
      await verify({
        phone: fullPhone(),
        otp: form.otp,
        address: form.address,
        aadhaarNumber: form.aadhaarNumber,
      });
      navigate("/");
    } catch (err) {
      setError(err.message || "Verification failed");
    }
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
          {error && <div className="text-danger small mb-2">{error}</div>}
          <form onSubmit={handleSubmit} className="d-flex flex-column gap-2">
            <div className="d-flex gap-2">
              <input
                className="input-brand flex-grow-1"
                name="phone"
                placeholder="Phone (OTP will be sent)"
                onChange={handleChange}
                disabled={phoneVerified}
                required
              />
              {!phoneVerified && (
                <button type="button" className="btn-brand-outline" onClick={handleSendOtp}>
                  {otpSent ? "Resend OTP" : "Send OTP"}
                </button>
              )}
              {phoneVerified && <span className="text-success align-self-center">✓ Verified</span>}
            </div>

            {otpSent && !phoneVerified && (
              <div className="d-flex gap-2">
                <input
                  className="input-brand flex-grow-1"
                  name="otp"
                  placeholder="Enter OTP"
                  onChange={handleChange}
                  required
                />
                <button type="button" className="btn-brand-outline" onClick={handleVerifyOtp}>
                  Verify OTP
                </button>
              </div>
            )}

            <input className="input-brand" name="address" placeholder="Address" onChange={handleChange} required />
            <input className="input-brand" name="aadhaarNumber" placeholder="Aadhaar Card Number" onChange={handleChange} required />
            <button className="btn-warn mt-2" disabled={!phoneVerified}>Verify</button>
          </form>
        </div>
      </div>
    </div>
  );
}
