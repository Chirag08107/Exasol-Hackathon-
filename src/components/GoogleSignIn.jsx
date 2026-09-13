import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const GoogleSignIn = ({ text = "signin_with" }) => {
  const buttonRef = useRef(null);
  const navigate = useNavigate();
  const { googleLogin } = useAuth();

  useEffect(() => {
    if (!window.google || !buttonRef.current) {
      return;
    }

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

    window.google.accounts.id.renderButton(
      buttonRef.current,
      {
        theme: "outline",
        size: "large",
        text: text,
        shape: "rectangular",
        logo_alignment: "left",
        width: 350,
      }
    );
  }, [googleLogin, navigate, text]);

    return <div className="google-signin-container">
        <div ref={buttonRef}></div></div>;
};

export default GoogleSignIn;