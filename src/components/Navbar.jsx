import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function initials(user) {
  const name = [user?.firstName, user?.lastName].filter(Boolean).join(" ") || user?.userName || "U";
  return name
    .trim()
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function Navbar() {
  const { user, logout, updateProfile } = useAuth();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [form, setForm] = useState({ firstName: "", middleName: "", lastName: "", address: "" });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate("/login");
  };

  const openUpdateModal = () => {
    setMenuOpen(false);
    setForm({
      firstName: user?.firstName || "",
      middleName: user?.middleName || "",
      lastName: user?.lastName || "",
      address: user?.address || "",
    });
    setSaveError("");
    setSaveSuccess(false);
    setShowUpdateModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveError("");

    try {
      await updateProfile(form);
      setSaveSuccess(true);
    } catch (err) {
      setSaveError(err.message || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <nav className="nav-brand">
        <Link to="/" className="nav-logo">FormSahay</Link>
        <Link to="/about" className="nav-link-quiet">About us</Link>

        {!user && (
          <div className="nav-actions">
            <Link to="/signup" className="btn-brand-outline">Sign Up</Link>
            <Link to="/login" className="btn-brand">Login</Link>
          </div>
        )}

        {user && !user.isVerified && (
          <div className="nav-actions">
            <Link to="/verify" className="btn-warn">Verify Yourself</Link>
            <button className="btn-ghost" onClick={handleLogout}>Log Out</button>
          </div>
        )}

        {user && user.isVerified && (
          <div className="nav-profile" ref={menuRef}>
            <button className="nav-profile-btn" onClick={() => setMenuOpen((o) => !o)}>
              <span className="nav-avatar">{initials(user)}</span>
              <span>{user.firstName}</span>
              <span className="nav-caret">▾</span>
            </button>

            {menuOpen && (
              <div className="nav-dropdown">
                <button className="nav-dropdown-item" onClick={openUpdateModal}>Update details</button>
                <button className="nav-dropdown-item" onClick={handleLogout}>Log out</button>
              </div>
            )}
          </div>
        )}
      </nav>

      {showUpdateModal && (
        <div className="modal-overlay" onClick={() => setShowUpdateModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h5 className="mb-3">Update your details</h5>

            {saveError && <div className="text-danger small mb-2">{saveError}</div>}
            {saveSuccess && <div className="text-success small mb-2">Saved!</div>}

            <form onSubmit={handleSave} className="d-flex flex-column gap-2">
              <input
                className="input-brand"
                placeholder="First Name"
                value={form.firstName}
                onChange={(e) => setForm({ ...form, firstName: e.target.value })}
                required
              />
              <input
                className="input-brand"
                placeholder="Middle Name"
                value={form.middleName}
                onChange={(e) => setForm({ ...form, middleName: e.target.value })}
              />
              <input
                className="input-brand"
                placeholder="Last Name"
                value={form.lastName}
                onChange={(e) => setForm({ ...form, lastName: e.target.value })}
                required
              />
              <input
                className="input-brand"
                placeholder="Address"
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
              />
              <div className="d-flex gap-2 justify-content-end mt-2">
                <button type="button" className="btn-brand-outline" onClick={() => setShowUpdateModal(false)}>
                  Close
                </button>
                <button type="submit" className="btn-brand" disabled={saving}>
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
