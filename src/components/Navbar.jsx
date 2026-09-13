import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  /*
  ---------------------------------------------------------
  CLOSE DROPDOWN WHEN CLICKING OUTSIDE
  ---------------------------------------------------------
  */

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target)
      ) {
        setProfileOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  /*
  ---------------------------------------------------------
  LOGOUT
  ---------------------------------------------------------
  */

  const handleLogout = () => {
    setProfileOpen(false);
    logout();
    navigate("/login");
  };

  /*
  ---------------------------------------------------------
  DISPLAY NAME
  ---------------------------------------------------------
  */

  const getDisplayName = () => {
    if (!user) {
      return "User";
    }

    const fullName = [
      user.firstName,
      user.lastName,
    ]
      .filter(Boolean)
      .join(" ")
      .trim();

    if (fullName) {
      return fullName;
    }

    if (user.name) {
      return user.name;
    }

    if (user.userName) {
      return user.userName;
    }

    if (user.email) {
      return user.email.split("@")[0];
    }

    return "User";
  };

  /*
  ---------------------------------------------------------
  INITIALS
  ---------------------------------------------------------
  */

  const getInitials = () => {
    const displayName = getDisplayName();

    const parts = displayName
      .trim()
      .split(/\s+/)
      .filter(Boolean);

    if (parts.length >= 2) {
      return (
        parts[0][0] +
        parts[parts.length - 1][0]
      ).toUpperCase();
    }

    if (parts.length === 1) {
      return parts[0]
        .substring(0, 2)
        .toUpperCase();
    }

    return "U";
  };

  const displayName = getDisplayName();
  const initials = getInitials();

  return (
    <nav className="nav-brand d-flex align-items-center">

      {/* LOGO */}

      <Link
        to="/"
        className="nav-logo"
      >
        Logo
      </Link>

      {/* ABOUT */}

      <Link
        to="/about"
        className="nav-link-quiet ms-4 me-auto"
      >
        About us
      </Link>

      {/* =================================================
          NOT LOGGED IN
      ================================================= */}

      {!user && (
        <div className="d-flex gap-2">

          <Link
            to="/signup"
            className="btn-brand-outline"
          >
            Sign Up
          </Link>

          <Link
            to="/login"
            className="btn-brand"
          >
            Login
          </Link>

        </div>
      )}

      {/* =================================================
          LOGGED IN BUT NOT VERIFIED
      ================================================= */}

      {user && !user.isVerified && (
        <div
          className="d-flex gap-2 align-items-center"
          ref={profileRef}
        >

          <Link
            to="/verify"
            className="btn-warn"
          >
            Verify Yourself
          </Link>

          <div className="position-relative">

            <button
              type="button"
              className="btn-ghost d-flex align-items-center gap-2"
              onClick={() =>
                setProfileOpen(!profileOpen)
              }
            >

              {/* INITIALS CIRCLE */}

              <div
                className="rounded-circle d-flex align-items-center justify-content-center"
                style={{
                  width: "32px",
                  height: "32px",
                  border: "1px solid var(--line)",
                  fontSize: "13px",
                  fontWeight: "600",
                  flexShrink: 0,
                }}
              >
                {initials}
              </div>

              <span>
                {displayName}
              </span>

              <span
                style={{
                  fontSize: "11px",
                }}
              >
                {profileOpen ? "▲" : "▼"}
              </span>

            </button>

            {profileOpen && (
              <ProfileDropdown
                onLogout={handleLogout}
                onClose={() =>
                  setProfileOpen(false)
                }
              />
            )}

          </div>

        </div>
      )}

      {/* =================================================
          LOGGED IN AND VERIFIED
      ================================================= */}

      {user && user.isVerified && (
        <div
          className="position-relative"
          ref={profileRef}
        >

          <button
            type="button"
            className="btn-ghost d-flex align-items-center gap-2"
            onClick={() =>
              setProfileOpen(!profileOpen)
            }
          >

            {/* INITIALS CIRCLE */}

            <div
              className="rounded-circle d-flex align-items-center justify-content-center"
              style={{
                width: "32px",
                height: "32px",
                border: "1px solid var(--line)",
                fontSize: "13px",
                fontWeight: "600",
                flexShrink: 0,
              }}
            >
              {initials}
            </div>

            <span>
              {displayName}
            </span>

            <span
              style={{
                fontSize: "11px",
              }}
            >
              {profileOpen ? "▲" : "▼"}
            </span>

          </button>

          {profileOpen && (
            <ProfileDropdown
              onLogout={handleLogout}
              onClose={() =>
                setProfileOpen(false)
              }
            />
          )}

        </div>
      )}

    </nav>
  );
}


/*
=========================================================
PROFILE DROPDOWN
=========================================================
*/

function ProfileDropdown({
  onLogout,
  onClose,
}) {
  return (
    <div
      className="dropdown-menu show"
      style={{
        position: "absolute",
        right: 0,
        top: "calc(100% + 8px)",
        minWidth: "180px",
        zIndex: 1000,
      }}
    >

      <button
        className="dropdown-item"
        type="button"
        onClick={onClose}
      >
        Update
      </button>

      <button
        className="dropdown-item"
        type="button"
        onClick={onLogout}
      >
        Log Out
      </button>

      <button
        className="dropdown-item text-danger"
        type="button"
        onClick={onClose}
      >
        Delete Account
      </button>

    </div>
  );
}