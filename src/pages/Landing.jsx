import { useEffect, useRef, useState } from "react";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";

const CATEGORIES = [
  { icon: "🪪", label: "Aadhaar Update" },
  { icon: "🛂", label: "Passport Application" },
  { icon: "💳", label: "PAN Card" },
  { icon: "🧾", label: "ITR-1 Filing" },
  { icon: "🚗", label: "Driving License" },
  { icon: "🏦", label: "Bank KYC" },
];

const POPULAR_FORMS = [
  { title: "PAN Card (Form 49AA)", meta: "Tax & Finance · ~10 min" },
  { title: "Aadhaar Registration", meta: "Identity & Travel · ~8 min" },
  { title: "Passport Application", meta: "Identity & Travel · ~15 min" },
  { title: "ITR-1 Filing", meta: "Tax & Finance · ~20 min" },
];

const HISTORY = [
  { label: "Passport renewal steps", active: true },
  { label: "PAN card correction" },
  { label: "GST registration help" },
];

function replyFor(text) {
  const lower = text.toLowerCase();
  if (lower.includes("pan")) {
    return "For a PAN Card (Form 49AA) you'll need proof of identity, proof of address, and a passport-size photo. Once the backend is connected I'll walk you through each field and flag common mistakes before you submit.";
  }
  if (lower.includes("passport")) {
    return "Passport applications need proof of address, date of birth, and (for most categories) an Aadhaar reference. I can break this into a short checklist once the live form engine is wired up.";
  }
  if (lower.includes("aadhaar")) {
    return "Aadhaar updates depend on what you're changing — address, phone, or biometric. Tell me which one and I'll outline the exact document list.";
  }
  if (lower.includes("itr") || lower.includes("tax")) {
    return "ITR-1 is for salaried individuals with income under ₹50L. I'll eventually pull your prefilled data automatically — for now, here's the doc checklist we'll need.";
  }
  return "Got it — once the backend is live, I'll look that up against our 80-form knowledge base and give you a step-by-step checklist with the exact documents and common mistakes to avoid.";
}

export default function Landing() {
  const { user } = useAuth();
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const sendMessage = (text) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setMessage("");
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages((prev) => [...prev, { role: "assistant", text: replyFor(trimmed) }]);
    }, 900);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(message);
  };

  const started = messages.length > 0;

  return (
    <div className="d-flex flex-column vh-100">
      <Navbar />
      <div className="d-flex flex-grow-1 overflow-hidden">
        <aside className="side-rail border-end p-3 d-none d-lg-flex" style={{ width: 240 }}>
          <button className="btn-brand-outline w-100" onClick={() => setMessages([])}>
            + New Chat
          </button>

          <div className="side-rail-label">Recent</div>
          {HISTORY.map((h) => (
            <div key={h.label} className={`side-item ${h.active ? "active" : ""}`}>
              <span className="side-item-icon">💬</span>
              <span className="text-truncate">{h.label}</span>
            </div>
          ))}

          <div className="mt-auto pt-3" style={{ borderTop: "1px solid var(--line)" }}>
            {user ? (
              <div className="side-item-icon" style={{ fontSize: "0.78rem", color: "var(--ink-soft)" }}>
                Signed in as <strong style={{ color: "var(--ink)" }}>{user.firstName}</strong>
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
                  Tell FormSahay which form you're stuck on — PAN, Aadhaar, passport, ITR,
                  and more — and get a plain-language checklist, the exact documents you need,
                  and the mistakes to avoid before you submit.
                </p>

                <div className="d-flex flex-wrap justify-content-center gap-2 mb-4">
                  {CATEGORIES.map((c) => (
                    <button
                      key={c.label}
                      type="button"
                      className="chip"
                      onClick={() => sendMessage(`Help me with ${c.label}`)}
                    >
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
                {messages.map((m, i) => (
                  <div key={i} className={`chat-row from-${m.role}`}>
                    {m.role === "assistant" && <div className="chat-avatar">✦</div>}
                    <div className="chat-bubble">{m.text}</div>
                  </div>
                ))}
                {isTyping && (
                  <div className="chat-row from-assistant">
                    <div className="chat-avatar">✦</div>
                    <div className="chat-bubble">
                      <span className="typing-dots"><span /><span /><span /></span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mx-auto w-100" style={{ maxWidth: 760 }}>
            <div className="chat-input-row">
              <input
                className="chat-input-plain"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about any government form..."
              />
              <button className="send-btn btn-brand" style={{ borderRadius: "50%", width: 40, height: 40, padding: 0 }} disabled={!message.trim()}>
                ↑
              </button>
            </div>
            <p className="chat-disclaimer">
              Frontend draft — replies are simulated until the Exasol-backed engine is connected.
            </p>
          </form>
        </main>

        <aside className="side-rail border-start p-3 d-none d-xl-flex" style={{ width: 260 }}>
          <div className="side-rail-label" style={{ marginTop: 0 }}>Popular forms</div>
          {POPULAR_FORMS.map((f) => (
            <div
              key={f.title}
              className="popular-form-card"
              onClick={() => sendMessage(`Help me with ${f.title}`)}
            >
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
