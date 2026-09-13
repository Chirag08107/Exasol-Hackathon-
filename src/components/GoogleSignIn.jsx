import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const GoogleSignIn = ({ text = "signin_with" }) => {
  const buttonRef = useRef(null);
  const navigate = useNavigate();
  const { googleLogin } = useAuth();

  useEffect(() => {
    if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) {
      console.warn(
        "VITE_GOOGLE_CLIENT_ID is not set — Google Sign-In button will not render. See .env.local."
      );
      return;
    }

    let cancelled = false;

    function render() {
      if (cancelled || !buttonRef.current) return;

      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,

        callback: async (response) => {
          try {
            await googleLogin(response.credential);
            navigate("/");
          } catch (error) {
            console.error("Google login failed:", error);
            alert(error.message);
          }
        },
      });

      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
        text,
        shape: "rectangular",
        logo_alignment: "left",
        width: 350,
      });
    }

    // The Google Identity Services script is loaded with async/defer,
    // so it may not be ready yet when this component first mounts.
    // Poll briefly until window.google shows up instead of silently
    // giving up (which is what caused the button to never render).
    if (window.google?.accounts?.id) {
      render();
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          render();
        }
      }, 100);

      const timeout = setTimeout(() => clearInterval(interval), 10000);

      return () => {
        cancelled = true;
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }

    return () => {
      cancelled = true;
    };
  }, [googleLogin, navigate, text]);

  return (
    <div className="google-signin-container">
      <div ref={buttonRef}></div>
    </div>
  );
};

export default GoogleSignIn;
