import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function initialsOf(name) {
  if (!name) return "U";
  return name.trim().slice(0, 2).toUpperCase();
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
    setMenuOpen(false);
  };

  return (
    <nav className="nav-brand">
      <Link to="/" className="nav-logo">
        <span className="nav-logo-mark">FS</span>
        <span className="nav-logo-text">
          <span className="font-display" style={{ fontSize: "1.15rem" }}>FormSahay</span>
          <span className="nav-logo-tagline">Government forms, simplified</span>
        </span>
      </Link>

      <NavLink
        to="/about"
        className={({ isActive }) => `nav-link-quiet nav-desktop-only ms-4 me-auto ${isActive ? "active" : ""}`}
      >
        About us
      </NavLink>
      <div className="me-auto d-none" />

      <button
        className="nav-mobile-toggle ms-auto"
        onClick={() => setMenuOpen((o) => !o)}
        aria-label="Toggle menu"
      >
        {menuOpen ? "✕" : "☰"}
      </button>

      <div className="d-flex gap-2 align-items-center nav-desktop-only">
        {!user && (
          <>
            <Link to="/signup" className="btn-brand-outline">Sign Up</Link>
            <Link to="/login" className="btn-brand">Login</Link>
          </>
        )}

        {user && !user.isVerified && (
          <>
            <Link to="/verify" className="btn-warn">Verify Yourself</Link>
            <button className="btn-ghost" onClick={handleLogout}>Log Out</button>
          </>
        )}

        {user && user.isVerified && (
          <div className="dropdown">
            <button
              className="btn-ghost d-flex align-items-center gap-2 dropdown-toggle"
              data-bs-toggle="dropdown"
            >
              <span className="avatar-initials">{initialsOf(user.firstName || user.userName)}</span>
              {user.firstName}
            </button>
            <ul className="dropdown-menu dropdown-menu-end">
              <li><button className="dropdown-item">Update profile</button></li>
              <li><button className="dropdown-item" onClick={handleLogout}>Log Out</button></li>
              <li><hr className="dropdown-divider" /></li>
              <li><button className="dropdown-item text-danger">Delete account</button></li>
            </ul>
          </div>
        )}
      </div>

      {menuOpen && (
        <div
          className="w-100 mt-3 pt-3 d-flex flex-column gap-2"
          style={{ borderTop: "1px solid var(--line)" }}
        >
          <Link to="/about" className="nav-link-quiet" onClick={() => setMenuOpen(false)}>About us</Link>

          {!user && (
            <>
              <Link to="/login" className="btn-brand text-center" onClick={() => setMenuOpen(false)}>Login</Link>
              <Link to="/signup" className="btn-brand-outline text-center" onClick={() => setMenuOpen(false)}>Sign Up</Link>
            </>
          )}

          {user && !user.isVerified && (
            <>
              <Link to="/verify" className="btn-warn text-center" onClick={() => setMenuOpen(false)}>Verify Yourself</Link>
              <button className="btn-brand-outline" onClick={handleLogout}>Log Out</button>
            </>
          )}

          {user && user.isVerified && (
            <>
              <div className="d-flex align-items-center gap-2">
                <span className="avatar-initials">{initialsOf(user.firstName || user.userName)}</span>
                <span>{user.firstName}</span>
              </div>
              <button className="btn-brand-outline" onClick={handleLogout}>Log Out</button>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
