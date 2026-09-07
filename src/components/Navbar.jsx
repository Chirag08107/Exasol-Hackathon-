import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="nav-brand d-flex align-items-center">
      <Link to="/" className="nav-logo">Logo</Link>
      <Link to="/about" className="nav-link-quiet ms-4 me-auto">About us</Link>

      {!user && (
        <div className="d-flex gap-2">
          <Link to="/signup" className="btn-brand-outline">Sign Up</Link>
          <Link to="/login" className="btn-brand">Login</Link>
        </div>
      )}

      {user && !user.isVerified && (
        <div className="d-flex gap-2 align-items-center">
          <Link to="/verify" className="btn-warn">Verify Yourself</Link>
          <Link to="/login" className="btn-brand">Login</Link>
        </div>
      )}

      {user && user.isVerified && (
        <div className="dropdown">
          <button
            className="btn-ghost d-flex align-items-center gap-2 dropdown-toggle"
            data-bs-toggle="dropdown"
          >
            <img
              src={user.profilePhoto || "https://via.placeholder.com/32"}
              alt="profile"
              width="32"
              height="32"
              className="rounded-circle"
              style={{ border: "1px solid var(--line)" }}
            />
            {user.firstName}
          </button>
          <ul className="dropdown-menu dropdown-menu-end">
            <li><button className="dropdown-item">Update</button></li>
            <li><button className="dropdown-item" onClick={handleLogout}>Log Out</button></li>
            <li><button className="dropdown-item text-danger">Delete Account</button></li>
          </ul>
        </div>
      )}
    </nav>
  );
}
