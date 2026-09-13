import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";
import { searchForms, createSession, getSession, submitAnswer } from "../services/api";

const CATEGORIES = [
  { icon: "🪪", label: "Aadhaar" },
  { icon: "🛂", label: "Passport" },
  { icon: "💳", label: "PAN Card" },
  { icon: "🧾", label: "ITR" },
  { icon: "🚗", label: "Driving License" },
  { icon: "🏦", label: "Bank KYC" },
];

const POPULAR_FORMS = [
  { title: "PAN Card", meta: "Tax & Finance" },
  { title: "Aadhaar Registration", meta: "Identity & Travel" },
  { title: "Passport Application", meta: "Identity & Travel" },
  { title: "ITR-1 Filing", meta: "Tax & Finance" },
];

const HISTORY = [
  { label: "Passport renewal steps", active: true },
  { label: "PAN card correction" },
  { label: "GST registration help" },
];

export default function Landing() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [message, setMessage] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showVerifyPopup, setShowVerifyPopup] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const [selectedForm, setSelectedForm] = useState(null);
  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");

  const inputRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [results, session, loading, error]);

  async function runSearch(query) {
    const trimmed = query.trim();
    if (!trimmed) return;

    setMessage(trimmed);
    setLoading(true);
    setError("");
    setHasSearched(true);
    setResults([]);

    try {
      const data = await searchForms(trimmed);
      setResults(data.results || []);
    } catch (err) {
      setError(err.message || "Unable to search forms. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    runSearch(message);
  };

  async function handleSelectForm(form) {
    if (!user?.isVerified && !user?.verified) {
      setShowVerifyPopup(true);
      return;
    }

    setLoading(true);
    setError("");

    try {
      setSelectedForm(form);

      const data = await createSession(form.form_id);
      const sessionId = data.session_id || data.sessionId || data.id || data.session?.session_id;

      if (!sessionId) {
        throw new Error("Session was created, but no session ID was returned.");
      }

      const sessionData = await getSession(sessionId);
      setSession(sessionData);
      setAnswer("");
      setResults([]);
      setHasSearched(false);
    } catch (err) {
      if (err.message === "LOGIN_REQUIRED") {
        setError("Please login before starting a form.");
      } else {
        setError(err.message || "Unable to start the form.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleContinue() {
    if (!session || !session.current_field) return;
    const fieldId = session.current_field.field_id;

    if (!answer.trim()) {
      setError("Please enter an answer before continuing.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await submitAnswer(session.session_id, fieldId, answer);

      if (!data.session) {
        throw new Error("Answer was saved, but updated session data was not returned.");
      }

      setSession(data.session);
      setAnswer("");
    } catch (err) {
      if (err.message === "LOGIN_REQUIRED") {
        setError("Please login before continuing.");
      } else {
        setError(err.message || "Unable to submit your answer.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleNewChat() {
    setMessage("");
    setResults([]);
    setError("");
    setHasSearched(false);
    setSelectedForm(null);
    setSession(null);
    setAnswer("");
    setTimeout(() => inputRef.current?.focus(), 0);
  }

  const started = hasSearched || session;
  const progress = session?.progress;
  const progressPct = progress?.total ? (progress.completed / progress.total) * 100 : 0;

  return (
    <div className="d-flex flex-column vh-100">
      {showVerifyPopup && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(22, 35, 31, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div className="auth-card" style={{ background: "var(--surface)", borderRadius: "var(--radius)", padding: "2rem", boxShadow: "0 12px 40px rgba(22,35,31,0.25)" }}>
            <h4 className="mb-2">Verify yourself first</h4>
            <p style={{ color: "var(--ink-soft)" }}>
              You'll need to verify your identity before we can help you fill out a government form.
            </p>
            <div className="d-flex gap-2 justify-content-end mt-3">
              <button type="button" className="btn-ghost" onClick={() => setShowVerifyPopup(false)}>Cancel</button>
              <button type="button" className="btn-warn" onClick={() => { setShowVerifyPopup(false); navigate("/verify"); }}>
                Verify Now
              </button>
            </div>
          </div>
        </div>
      )}

      <Navbar />
      <div className="d-flex flex-grow-1 overflow-hidden">
        <aside className="side-rail border-end p-3 d-none d-lg-flex" style={{ width: 240 }}>
          <button className="btn-brand-outline w-100" onClick={handleNewChat}>+ New Chat</button>

          <div className="side-rail-label">Recent</div>
          {HISTORY.map((h) => (
            <div key={h.label} className={`side-item ${h.active ? "active" : ""}`}>
              <span className="side-item-icon">💬</span>
              <span className="text-truncate">{h.label}</span>
            </div>
          ))}

          <div className="mt-auto pt-3" style={{ borderTop: "1px solid var(--line)" }}>
            {user ? (
              <div style={{ fontSize: "0.78rem", color: "var(--ink-soft)" }}>
                Signed in as <strong style={{ color: "var(--ink)" }}>{user.firstName || user.userName}</strong>
                {!(user.isVerified || user.verified) && (
                  <div className="badge-warn mt-2 d-inline-block">Not verified</div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: "0.78rem", color: "var(--ink-soft)" }}>
                Sign in to save your chats and prefill your forms.
              </div>
            )}
          </div>
        </aside>

        <main className="flex-grow-1 d-flex flex-column p-3 p-md-4 overflow-hidden">
          {!started ? (
            <div className="flex-grow-1 d-flex align-items-center justify-content-center overflow-auto py-4">
              <div className="hero-wrap">
                <span className="hero-eyebrow">🇮🇳 80+ Indian government forms supported</span>
                <h1 className="hero-title">
                  Government paperwork,<br />
                  <span className="accent-word">finally made simple.</span>
                </h1>
                <p className="hero-subtitle">
                  Search for the form you're stuck on — PAN, Aadhaar, passport, ITR, and more —
                  and FormSahay will walk you through it field by field.
                </p>

                <div className="d-flex flex-wrap justify-content-center gap-2 mb-4">
                  {CATEGORIES.map((c) => (
                    <button key={c.label} type="button" className="chip" onClick={() => runSearch(c.label)}>
                      <span className="chip-icon">{c.icon}</span>
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div ref={scrollRef} className="chat-scroll flex-grow-1 py-2">
              <div className="mx-auto" style={{ maxWidth: 760 }}>
                {message && (
                  <div className="chat-row from-user">
                    <div className="chat-bubble">{message}</div>
                  </div>
                )}

                {loading && (
                  <div className="chat-row from-assistant">
                    <div className="chat-avatar">✦</div>
                    <div className="chat-bubble">
                      <span className="typing-dots"><span /><span /><span /></span>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="chat-row from-assistant">
                    <div className="chat-avatar">✦</div>
                    <div className="chat-bubble" style={{ borderColor: "var(--warn)", color: "var(--warn)" }}>
                      ⚠ {error}
                    </div>
                  </div>
                )}

                {!loading && !error && !session && hasSearched && (
                  <div className="chat-row from-assistant">
                    <div className="chat-avatar">✦</div>
                    <div className="chat-bubble">
                      {results.length > 0
                        ? `I found ${results.length} matching form${results.length === 1 ? "" : "s"}. Pick one to get started:`
                        : "I couldn't find a matching form. Try a different keyword — e.g. \"passport\" or \"PAN card\"."}
                    </div>
                  </div>
                )}

                {!loading && results.length > 0 && (
                  <div className="mb-3" style={{ marginLeft: "2.4rem" }}>
                    <div className="d-flex flex-column gap-2">
                      {results.map((form) => (
                        <div key={form.form_id} className="popular-form-card" onClick={() => handleSelectForm(form)}>
                          <div className="flex-grow-1">
                            <div className="popular-form-title">{form.form_name}</div>
                            <div className="popular-form-meta">
                              {form.form_code}{form.category ? ` · ${form.category}` : ""}
                            </div>
                            {form.description && (
                              <div className="popular-form-meta mt-1">{form.description}</div>
                            )}
                          </div>
                          <button type="button" className="btn-brand" style={{ flexShrink: 0 }}>
                            Select
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {session && selectedForm && (
                  <>
                    {progress && (
                      <div className="mb-3" style={{ marginLeft: "2.4rem", maxWidth: 460 }}>
                        <div className="d-flex justify-content-between mb-1" style={{ fontSize: "0.8rem", color: "var(--ink-soft)" }}>
                          <span>{selectedForm.form_name}</span>
                          <span>{progress.completed || 0} / {progress.total || 0}</span>
                        </div>
                        <div style={{ height: 6, borderRadius: 999, background: "var(--line)", overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${progressPct}%`, background: "var(--accent)", transition: "width 0.3s ease" }} />
                        </div>
                      </div>
                    )}

                    {session.current_field && !loading && (
                      <div className="chat-row from-assistant">
                        <div className="chat-avatar">✦</div>
                        <div className="chat-bubble">
                          <strong>{session.current_field.field_label}</strong>
                          {session.current_field.explanation && (
                            <div className="mt-1" style={{ fontSize: "0.88rem", color: "var(--ink-soft)" }}>
                              {session.current_field.explanation}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {!session.current_field && (
                      <div className="chat-row from-assistant">
                        <div className="chat-avatar">✦</div>
                        <div className="chat-bubble">This form has been completed! 🎉</div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {session && session.current_field ? (
            <form
              onSubmit={(e) => { e.preventDefault(); handleContinue(); }}
              className="mx-auto w-100"
              style={{ maxWidth: 760 }}
            >
              <div className="chat-input-row">
                <input
                  className="chat-input-plain"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder={session.current_field.example_value || "Type your answer..."}
                  disabled={loading}
                />
                <button className="send-btn btn-brand" style={{ borderRadius: "50%", width: 40, height: 40, padding: 0 }} disabled={!answer.trim() || loading}>
                  ↑
                </button>
              </div>
            </form>
          ) : !session && (
            <form onSubmit={handleSubmit} className="mx-auto w-100" style={{ maxWidth: 760 }}>
              <div className="chat-input-row">
                <input
                  ref={inputRef}
                  className="chat-input-plain"
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value);
                    if (hasSearched) {
                      setHasSearched(false);
                      setResults([]);
                      setError("");
                    }
                  }}
                  placeholder="Search for a government form..."
                  disabled={loading}
                />
                <button className="send-btn btn-brand" style={{ borderRadius: "50%", width: 40, height: 40, padding: 0 }} disabled={!message.trim() || loading}>
                  ↑
                </button>
              </div>
              <p className="chat-disclaimer">
                Connected to the FormSahay backend — results depend on the live Exasol form database.
              </p>
            </form>
          )}
        </main>

        <aside className="side-rail border-start p-3 d-none d-xl-flex" style={{ width: 260 }}>
          <div className="side-rail-label" style={{ marginTop: 0 }}>Popular forms</div>
          {POPULAR_FORMS.map((f) => (
            <div key={f.title} className="popular-form-card" onClick={() => runSearch(f.title)}>
              <div>
                <div className="popular-form-title">{f.title}</div>
                <div className="popular-form-meta">{f.meta}</div>
              </div>
            </div>
          ))}
        </aside>
      </div>
      <footer className="app-footer p-2 text-center">
        © {new Date().getFullYear()} FormSahay — Built for the Exasol Hackathon
      </footer>
    </div>
  );
}
