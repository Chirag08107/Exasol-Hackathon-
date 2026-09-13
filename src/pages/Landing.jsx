import { useEffect, useRef, useState } from "react";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";
import { searchForms, createSession, getSession, submitAnswer, getSessionPdf } from "../services/api";

const QUICK_LINKS = [
  { icon: "💳", label: "PAN Card", query: "PAN card" },
  { icon: "🪪", label: "Aadhaar", query: "Aadhaar" },
  { icon: "🛂", label: "Passport", query: "Passport" },
  { icon: "🚗", label: "Driving License", query: "Driving License" },
];

export default function Landing() {
  const { user } = useAuth();

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showVerifyPopup, setShowVerifyPopup] = useState(false);

  const [results, setResults] = useState(null);
  const [selectedForm, setSelectedForm] = useState(null);
  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");

  // Conversation history: {role: 'ai'|'user', text, fieldId?, options?}
  const [history, setHistory] = useState([]);

  const [pdfUrl, setPdfUrl] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [results, session, loading, error, pdfUrl, pdfLoading, history]);

  const started = Boolean(results || session);

  // Whenever the backend hands us a new current_field, append it to the
  // conversation as an "ai" turn (once — not on every re-render).
  useEffect(() => {
    const field = session?.current_field;
    if (!field) return;

    setHistory((h) => {
      const alreadyAsked = h.some((item) => item.role === "ai" && item.fieldId === field.field_id);
      if (alreadyAsked) return h;

      return [
        ...h,
        {
          role: "ai",
          fieldId: field.field_id,
          text: field.field_label,
          explanation: field.explanation,
          options: field.options,
        },
      ];
    });
  }, [session?.current_field?.field_id]);

  async function handleSearch(query) {
    const trimmed = query.trim();
    if (!trimmed) return;

    setMessage("");
    setLoading(true);
    setError("");
    setResults({ query: trimmed, forms: [] });

    try {
      const data = await searchForms(trimmed);
      setResults({ query: trimmed, forms: data.results || [] });
    } catch (err) {
      setError(err.message || "Unable to search forms.");
    } finally {
      setLoading(false);
    }
  }

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
      setResults(null);
      setAnswer("");
      setHistory([]);
    } catch (err) {
      setError(err.message === "LOGIN_REQUIRED" ? "Please login before starting a form." : (err.message || "Unable to start the form."));
    } finally {
      setLoading(false);
    }
  }

  async function submitFieldAnswer(value) {
    const trimmed = (value || "").trim();
    if (!session || !session.current_field || !trimmed) return;

    const field = session.current_field;

    setLoading(true);
    setError("");

    try {
      const data = await submitAnswer(session.session_id, field.field_id, trimmed);

      if (!data.session) {
        throw new Error("Answer was saved, but updated session data was not returned.");
      }

      // Only record the answer in the visible chat once the backend has
      // actually accepted it — an optimistic push here would show a
      // rejected/invalid answer as if it had been said.
      setHistory((h) => [...h, { role: "user", text: trimmed }]);
      setSession(data.session);
      setAnswer("");
    } catch (err) {
      setError(err.message === "LOGIN_REQUIRED" ? "Please login before continuing." : (err.message || "Unable to submit your answer."));
    } finally {
      setLoading(false);
    }
  }

  const formCompleted = Boolean(session) && !session.current_field;

  useEffect(() => {
    if (!formCompleted || pdfUrl || pdfLoading) return;

    let cancelled = false;

    (async () => {
      setPdfLoading(true);
      try {
        const { blob } = await getSessionPdf(session.session_id);
        if (!cancelled) setPdfUrl(URL.createObjectURL(blob));
      } catch (err) {
        if (!cancelled) setError(err.message || "Unable to generate the completed PDF.");
      } finally {
        if (!cancelled) setPdfLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formCompleted, session?.session_id]);

  function handleNewChat() {
    setMessage("");
    setResults(null);
    setSelectedForm(null);
    setSession(null);
    setAnswer("");
    setError("");
    setHistory([]);
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    setPdfUrl(null);
    setPdfLoading(false);
    setTimeout(() => inputRef.current?.focus(), 0);
  }

  function focusInput() {
    inputRef.current?.focus();
  }

  // The latest "ai" history entry is still awaiting an answer if no
  // "user" entry has been added after it yet.
  const lastEntry = history[history.length - 1];
  const awaitingOptionAnswer = lastEntry?.role === "ai" && lastEntry.options?.length > 0 && !loading;

  return (
    <div className="d-flex flex-column vh-100">
      {showVerifyPopup && (
        <div className="modal-overlay" onClick={() => setShowVerifyPopup(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h5 className="mb-2">Verify yourself first</h5>
            <p className="mb-3">You need to verify your identity before filling out a government form.</p>
            <div className="d-flex gap-2 justify-content-end">
              <button className="btn-brand-outline" onClick={() => setShowVerifyPopup(false)}>Cancel</button>
              <a className="btn-warn" href="/verify">Verify Now</a>
            </div>
          </div>
        </div>
      )}

      <Navbar />
      <div className="d-flex flex-grow-1 overflow-hidden">
        <main className="flex-grow-1 d-flex flex-column p-4">
          <div ref={scrollRef} className="flex-grow-1" style={{ overflowY: "auto" }}>
            {!started && (
              <div className="h-100 d-flex flex-column align-items-center justify-content-center text-center">
                <span className="hero-eyebrow">🇮🇳 Government forms, simplified</span>
                <span className="chat-prompt mt-3">What's in your mind?</span>
                <p className="hero-subtitle mt-2">
                  Search for the form you need — PAN, Aadhaar, passport, ITR, and more —
                  and I'll walk you through it field by field.
                </p>
              </div>
            )}

            {started && (
              <div className="d-flex flex-column gap-2">
                {results?.query && <div className="msg msg-user">{results.query}</div>}

                {loading && !session && <div className="msg msg-bot">Searching…</div>}

                {results && !loading && !error && (
                  <div className="msg msg-bot">
                    {results.forms.length === 0 ? (
                      <span>No matching forms found. Try a different keyword.</span>
                    ) : (
                      <div>
                        <div className="mb-2">Found {results.forms.length} matching form(s):</div>
                        <div className="d-flex flex-column gap-2">
                          {results.forms.map((form) => (
                            <div key={form.form_id} className="result-card">
                              <div>
                                <div style={{ fontWeight: 500 }}>{form.form_name}</div>
                                <div className="text-muted small">{form.form_code}{form.category ? ` · ${form.category}` : ""}</div>
                              </div>
                              <button className="btn-brand" onClick={() => handleSelectForm(form)}>Select</button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {session && selectedForm && (
                  <>
                    {session.progress && (
                      <div className="text-muted small">
                        {selectedForm.form_name} — {session.progress.completed || 0}/{session.progress.total || 0} answered
                      </div>
                    )}

                    {/* Full Q&A conversation, in order — AI question, then the user's reply, repeating. */}
                    {history.map((entry, i) =>
                      entry.role === "ai" ? (
                        <div key={`ai-${entry.fieldId}-${i}`} className="msg msg-bot">
                          <strong>{entry.text}</strong>
                          {entry.explanation && (
                            <div className="text-muted small mt-1">{entry.explanation}</div>
                          )}
                          {entry.options?.length > 0 && awaitingOptionAnswer && i === history.length - 1 && (
                            <div className="option-chip-row mt-2">
                              {entry.options.map((opt) => (
                                <button
                                  key={opt.option_id ?? opt.option_code ?? opt.option_label}
                                  type="button"
                                  className="option-chip"
                                  onClick={() => submitFieldAnswer(opt.option_code || opt.option_label)}
                                >
                                  {opt.option_label || opt.option_code}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div key={`user-${i}`} className="msg msg-user">{entry.text}</div>
                      )
                    )}

                    {!session.current_field && (
                      <div className="msg msg-bot">
                        {pdfLoading && <span>All fields are complete — generating your PDF…</span>}

                        {!pdfLoading && pdfUrl && (
                          <div>
                            <strong>Form ready! Please carefully check the completed form before submitting it.</strong>
                            <p className="text-muted small mt-1 mb-2">
                              Review all details carefully. If a hard copy is required, print and submit it
                              yourself. If an online upload is required, upload it yourself.
                            </p>
                            <div className="d-flex gap-2">
                              <a href={pdfUrl} target="_blank" rel="noreferrer" className="btn-brand">View PDF</a>
                              <a href={pdfUrl} download={`form_${session.session_id}.pdf`} className="btn-brand-outline">Download</a>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}

                {loading && session?.current_field && <div className="msg msg-bot">Saving…</div>}

                {error && <div className="msg msg-bot text-danger">{error}</div>}
              </div>
            )}
          </div>

          <form
            className="d-flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();

              if (session?.current_field) {
                submitFieldAnswer(answer);
              } else {
                handleSearch(message);
              }
            }}
          >
            <input
              ref={inputRef}
              className="chat-input flex-grow-1"
              value={session?.current_field ? answer : message}
              onChange={(e) => (session?.current_field ? setAnswer(e.target.value) : setMessage(e.target.value))}
              placeholder={
                awaitingOptionAnswer
                  ? "Pick an option above, or type it here..."
                  : session?.current_field
                  ? "Type your answer..."
                  : "Type a message..."
              }
              disabled={loading || formCompleted}
            />
            <button className="send-btn" disabled={loading || formCompleted}>↑</button>
          </form>
        </main>

        <aside className="side-rail border-start p-3" style={{ width: 220 }}>
          <button type="button" className="side-item side-item-btn mb-2" onClick={focusInput}>
            🔍 Search
          </button>

          {started && (
            <button type="button" className="side-item side-item-btn mb-3" onClick={handleNewChat}>
              + New chat
            </button>
          )}

          <div className="side-rail-label">Quick links</div>
          {QUICK_LINKS.map((q) => (
            <button key={q.label} type="button" className="side-item side-item-btn" onClick={() => handleSearch(q.query)}>
              {q.icon} {q.label}
            </button>
          ))}
        </aside>
      </div>
      <footer className="app-footer">
        <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 px-3 py-2">
          <span>© {new Date().getFullYear()} FormSahay — an assistant, not a filing service.</span>
          <span className="text-muted small">
            We help you fill the form. You review, print/upload, and submit it yourself.
          </span>
        </div>
      </footer>
    </div>
  );
}
