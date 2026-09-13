import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Verify() {
  const [form, setForm] = useState({
    phone: "",
    address: "",
    aadhaarNumber: "",
    otp: "",
  });

  const [otpSent, setOtpSent] = useState(false);
  const [phoneVerified, setPhoneVerified] =
    useState(false);

  const [resendTimer, setResendTimer] = useState(0);
  const [otpExpiryTimer, setOtpExpiryTimer] =
    useState(0);

  const [loading, setLoading] = useState(false);

  const [alert, setAlert] = useState({
    type: "",
    message: "",
  });

  const navigate = useNavigate();

  const {
    sendOtp,
    resendOtp,
    verifyOtp,
    verify,
  } = useAuth();

  useEffect(() => {
    if (
      resendTimer <= 0 &&
      otpExpiryTimer <= 0
    ) {
      return;
    }

    const timer = setInterval(() => {
      setResendTimer((time) =>
        time > 0 ? time - 1 : 0
      );

      setOtpExpiryTimer((time) =>
        time > 0 ? time - 1 : 0
      );
    }, 1000);

    return () => clearInterval(timer);
  }, [resendTimer, otpExpiryTimer]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(
      seconds / 60
    );

    const remainingSeconds =
      seconds % 60;

    return `${String(minutes).padStart(
      2,
      "0"
    )}:${String(remainingSeconds).padStart(
      2,
      "0"
    )}`;
  };

  const getFullPhoneNumber = () => {
    return `+91${form.phone}`;
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(
      /\D/g,
      ""
    );

    setForm((previousForm) => ({
      ...previousForm,
      phone: value.slice(0, 10),
    }));

    setPhoneVerified(false);
    setOtpSent(false);
  };

  const handleChange = (e) => {
    setForm((previousForm) => ({
      ...previousForm,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSendOtp = async () => {
    if (form.phone.length !== 10) {
      setAlert({
        type: "error",
        message:
          "Please enter a valid 10-digit phone number.",
      });
      return;
    }

    setLoading(true);

    setAlert({
      type: "",
      message: "",
    });

    try {
      const phone =
        getFullPhoneNumber();

      await sendOtp(phone);

      setOtpSent(true);
      setPhoneVerified(false);

      setForm((previousForm) => ({
        ...previousForm,
        otp: "",
      }));

      setResendTimer(60);
      setOtpExpiryTimer(300);

      setAlert({
        type: "success",
        message:
          "OTP sent successfully! Please check your phone.",
      });
    } catch (error) {
      setAlert({
        type: "error",
        message:
          error.message ||
          "Failed to send OTP.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (resendTimer > 0) {
      return;
    }

    setLoading(true);

    try {
      const phone =
        getFullPhoneNumber();

      await resendOtp(phone);

      setForm((previousForm) => ({
        ...previousForm,
        otp: "",
      }));

      setResendTimer(60);
      setOtpExpiryTimer(300);

      setAlert({
        type: "success",
        message:
          "OTP resent successfully!",
      });
    } catch (error) {
      setAlert({
        type: "error",
        message:
          error.message ||
          "Failed to resend OTP.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!form.otp.trim()) {
      setAlert({
        type: "error",
        message:
          "Please enter the OTP.",
      });
      return;
    }

    if (otpExpiryTimer <= 0) {
      setAlert({
        type: "error",
        message:
          "OTP has expired. Please resend the OTP.",
      });
      return;
    }

    setLoading(true);

    try {
      const phone =
        getFullPhoneNumber();

      await verifyOtp(
        phone,
        form.otp
      );

      setPhoneVerified(true);

      setAlert({
        type: "success",
        message:
          "Phone number verified successfully!",
      });
    } catch (error) {
      setAlert({
        type: "error",
        message:
          error.message ||
          "Invalid OTP. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!phoneVerified) {
      setAlert({
        type: "error",
        message:
          "Please verify your phone number first.",
      });
      return;
    }

    if (!form.address.trim()) {
      setAlert({
        type: "error",
        message:
          "Please enter your address.",
      });
      return;
    }

    if (
      form.aadhaarNumber.length !== 12
    ) {
      setAlert({
        type: "error",
        message:
          "Please enter a valid 12-digit Aadhaar number.",
      });
      return;
    }

    setLoading(true);

    try {
      await verify({
        phone: getFullPhoneNumber(),
        otp: form.otp,
        address: form.address,
        aadhaarNumber:
          form.aadhaarNumber,
      });

      setAlert({
        type: "success",
        message:
          "Verification completed successfully!",
      });

      setTimeout(() => {
        navigate("/");
      }, 1200);
    } catch (error) {
      setAlert({
        type: "error",
        message:
          error.message ||
          "Verification failed.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-visual">
        <p className="auth-visual-quote">
          One last step — this keeps your
          account and everyone else's secure.
        </p>
      </div>

      <div className="auth-form-col">
        <div className="auth-card">
          <div className="eyebrow">
            Almost there
          </div>

          <h2 className="mb-4">
            Verify Yourself
          </h2>

          {alert.message && (
            <div
              className={`alert ${
                alert.type === "success"
                  ? "alert-success"
                  : "alert-danger"
              }`}
            >
              {alert.type === "success"
                ? "✓ "
                : "⚠ "}
              {alert.message}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="d-flex flex-column gap-3"
          >
            <div>
              <div className="d-flex">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "0 12px",
                    border: "1px solid #dee2e6",
                    borderRight: "none",
                    borderRadius:
                      "8px 0 0 8px",
                    background: "#f8f9fa",
                    fontWeight: "500",
                    color: "#444",
                  }}
                >
                  +91
                </div>

                <input
                  className={`input-brand ${
                    phoneVerified
                      ? "border-success"
                      : ""
                  }`}
                  name="phone"
                  type="tel"
                  inputMode="numeric"
                  placeholder="Phone number"
                  value={form.phone}
                  onChange={
                    handlePhoneChange
                  }
                  disabled={
                    phoneVerified ||
                    loading
                  }
                  maxLength={10}
                  style={{
                    borderRadius:
                      "0 8px 8px 0",
                  }}
                  required
                />

                {phoneVerified && (
                  <span
                    style={{
                      marginLeft: "-35px",
                      marginTop: "8px",
                      zIndex: 2,
                      color: "green",
                      fontSize: "22px",
                      fontWeight: "bold",
                    }}
                  >
                    ✓
                  </span>
                )}
              </div>

              {!otpSent &&
                !phoneVerified && (
                  <button
                    type="button"
                    onClick={handleSendOtp}
                    className="btn btn-link p-0 text-decoration-none mt-1"
                    disabled={loading}
                  >
                    {loading
                      ? "Sending..."
                      : "Send OTP"}
                  </button>
                )}
            </div>

            {otpSent &&
              !phoneVerified && (
                <div>
                  <input
                    className="input-brand"
                    name="otp"
                    type="text"
                    inputMode="numeric"
                    placeholder="Enter OTP"
                    value={form.otp}
                    onChange={(e) =>
                      setForm(
                        (previousForm) => ({
                          ...previousForm,
                          otp: e.target.value
                            .replace(
                              /\D/g,
                              ""
                            )
                            .slice(0, 6),
                        })
                      )
                    }
                    maxLength={6}
                    disabled={loading}
                    required
                  />

                  <div
                    className="mt-1"
                    style={{
                      fontSize: "13px",
                      color: "#666",
                    }}
                  >
                    {otpExpiryTimer >
                    0 ? (
                      <>
                        OTP expires in{" "}
                        <strong>
                          {formatTime(
                            otpExpiryTimer
                          )}
                        </strong>
                      </>
                    ) : (
                      <span
                        style={{
                          color: "#dc3545",
                        }}
                      >
                        OTP has expired.
                      </span>
                    )}
                  </div>

                  <div className="mt-1">
                    {resendTimer > 0 ? (
                      <span
                        style={{
                          fontSize: "14px",
                          color: "#777",
                        }}
                      >
                        Resend OTP in{" "}
                        <strong>
                          {formatTime(
                            resendTimer
                          )}
                        </strong>
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={
                          handleResendOtp
                        }
                        className="btn btn-link p-0 text-decoration-none"
                        disabled={loading}
                      >
                        Resend OTP
                      </button>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={
                      handleVerifyOtp
                    }
                    className="btn btn-link p-0 text-decoration-none mt-1"
                    disabled={loading}
                  >
                    {loading
                      ? "Verifying..."
                      : "Verify OTP"}
                  </button>
                </div>
              )}

            <input
              className="input-brand"
              name="address"
              type="text"
              placeholder="Address"
              value={form.address}
              onChange={handleChange}
              disabled={loading}
              required
            />

            <input
              className="input-brand"
              name="aadhaarNumber"
              type="text"
              inputMode="numeric"
              placeholder="Aadhaar Card Number"
              value={
                form.aadhaarNumber
              }
              onChange={(e) =>
                setForm(
                  (previousForm) => ({
                    ...previousForm,
                    aadhaarNumber:
                      e.target.value
                        .replace(
                          /\D/g,
                          ""
                        )
                        .slice(0, 12),
                  })
                )
              }
              maxLength={12}
              disabled={loading}
              required
            />

            <button
              type="submit"
              className="btn-warn mt-2"
              disabled={
                !phoneVerified ||
                loading
              }
              style={{
                opacity:
                  phoneVerified &&
                  !loading
                    ? 1
                    : 0.6,
                cursor:
                  phoneVerified &&
                  !loading
                    ? "pointer"
                    : "not-allowed",
              }}
            >
              {loading
                ? "Verifying..."
                : "Verify"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}