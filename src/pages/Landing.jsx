import Navbar from "../components/Navbar";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import {
  searchForms,
  createSession,
  getSession,
  submitAnswer,
} from "../services/api";

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

  async function handleSearch() {
    const query = message.trim();

    if (!query) {
      return;
    }

    setLoading(true);
    setError("");
    setHasSearched(true);
    setResults([]);

    try {
      const data = await searchForms(query);

      console.log("Search response:", data);

      setResults(data.results || []);
    } catch (err) {
      console.error("Search error:", err);

      setError(
        err.message ||
          "Unable to search forms. Please try again."
      );
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
    console.log("Selected form:", form);

    setSelectedForm(form);

    const data = await createSession(form.form_id);

    console.log("Session creation response:", data);

    const sessionId =
      data.session_id ||
      data.sessionId ||
      data.id ||
      data.session?.session_id;

    console.log("Extracted session ID:", sessionId);

    if (!sessionId) {
      throw new Error(
        "Session was created, but no session ID was returned."
      );
    }

    const sessionData =
      await getSession(sessionId);

    console.log(
      "Session details:",
      sessionData
    );

    setSession(sessionData);
    setAnswer("");
    setResults([]);
    setHasSearched(false);
  } catch (err) {
    console.error(
      "Form selection error:",
      err
    );

    if (err.message === "LOGIN_REQUIRED") {
      setError(
        "Please login before starting a form."
      );
    } else {
      setError(
        err.message ||
          "Unable to start the form."
      );
    }
  } finally {
    setLoading(false);
  }
}

  async function handleContinue() {
    if (!session || !session.current_field) {
      return;
    }

    const fieldId =
      session.current_field.field_id;

    if (!answer.trim()) {
      setError(
        "Please enter an answer before continuing."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      console.log("Submitting answer:", {
        sessionId: session.session_id,
        fieldId: fieldId,
        value: answer,
      });

      const data = await submitAnswer(
        session.session_id,
        fieldId,
        answer
      );

      console.log("Answer response:", data);

      if (!data.session) {
        throw new Error(
          "Answer was saved, but updated session data was not returned."
        );
      }

      console.log("Updated session:", data.session);

      setSession(data.session);
      setAnswer("");
    } catch (err) {
      console.error(
        "Answer submission error:",
        err
      );

      if (err.message === "LOGIN_REQUIRED") {
        setError(
          "Please login before continuing."
        );
      } else {
        setError(
          err.message ||
            "Unable to submit your answer."
        );
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

    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  }

  function focusSearch() {
    inputRef.current?.focus();
  }

  return (
    <div className="d-flex flex-column vh-100">
      {showVerifyPopup && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "white",
              borderRadius: "12px",
              padding: "30px",
              width: "min(420px, 90%)",
              boxShadow:
                "0 10px 30px rgba(0, 0, 0, 0.2)",
              textAlign: "center",
            }}
          >
            <h4 className="mb-3">
              Verify Yourself
            </h4>

            <p className="text-muted mb-4">
              Please verify yourself before filling
              a government form.
            </p>

            <div className="d-flex gap-2 justify-content-center">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() =>
                  setShowVerifyPopup(false)
                }
              >
                Cancel
              </button>

              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  setShowVerifyPopup(false);
                  navigate("/verify");
                }}
              >
                Verify Now
              </button>
            </div>
          </div>
        </div>
      )}
      <Navbar />

      <div className="d-flex flex-grow-1 overflow-hidden">
        <aside
          className="side-rail border-end p-3"
          style={{ width: 220 }}
        >
          <button
            className="btn-brand-outline w-100 mb-3"
            onClick={handleNewChat}
          >
            + New Chat
          </button>

          <div className="side-item">
            Option 1
          </div>

          <div className="side-item">
            Option 2
          </div>

          <div className="side-item">
            Option 3
          </div>
        </aside>

        <main className="flex-grow-1 d-flex flex-column p-4">
          <div className="flex-grow-1 overflow-auto">
            {session && selectedForm && (
              <div>
                <div className="mb-4">
                  <h3>
                    {selectedForm.form_name}
                  </h3>

                  <p className="text-muted">
                    Let's fill out this form step by
                    step.
                  </p>
                </div>

                {session.progress && (
                  <div className="mb-4">
                    <div className="d-flex justify-content-between">
                      <span>
                        Progress
                      </span>

                      <span>
                        {session.progress.completed || 0}{" "}
                        /{" "}
                        {session.progress.total || 0}
                      </span>
                    </div>

                    <div className="progress mt-2">
                      <div
                        className="progress-bar"
                        style={{
                          width: `${
                            session.progress.total
                              ? (
                                  (session.progress.completed /
                                    session.progress.total) *
                                  100
                                )
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                )}

                {session.current_field && (
                  <div className="border rounded p-4">
                    <h5 className="mb-3">
                      {session.current_field.field_label}
                    </h5>

                    {session.current_field.explanation && (
                      <p className="text-muted">
                        {
                          session.current_field
                            .explanation
                        }
                      </p>
                    )}

                    <p className="small text-muted">
                      Field type:{" "}
                      {
                        session.current_field
                          .field_type
                      }
                    </p>

                    <input
                      type="text"
                      className="form-control"
                      value={answer}
                      onChange={(e) =>
                        setAnswer(e.target.value)
                      }
                      placeholder={
                        session.current_field
                          .example_value ||
                        "Enter your answer"
                      }
                    />

                    <button
                      className="btn btn-primary mt-3"
                      type="button"
                      onClick={handleContinue}
                      disabled={loading}
                    >
                      {loading
                        ? "Saving..."
                        : "Continue"}
                    </button>
                  </div>
                )}

                {!session.current_field && (
                  <div className="alert alert-success">
                    This form has been completed! 🎉
                  </div>
                )}
              </div>
            )}

            {!hasSearched &&
              !session &&
              !loading && (
                <div className="h-100 d-flex align-items-center justify-content-center">
                  <span className="chat-prompt">
                    What's in your mind?
                  </span>
                </div>
              )}

            {loading && (
              <div className="d-flex justify-content-center align-items-center p-4">
                <span>
                  Please wait...
                </span>
              </div>
            )}

            {error && (
              <div className="alert alert-danger">
                {error}
              </div>
            )}

            {!loading &&
              results.length > 0 && (
                <div>
                  <h4 className="mb-3">
                    Matching Forms
                  </h4>

                  <div className="d-flex flex-column gap-3">
                    {results.map((form) => (
                      <div
                        key={form.form_id}
                        className="border rounded p-3"
                      >
                        <h5>
                          {form.form_name}
                        </h5>

                        <div className="text-muted small">
                          Form Code:{" "}
                          {form.form_code}
                        </div>

                        {form.category && (
                          <div className="small mt-1">
                            Category:{" "}
                            {form.category}
                          </div>
                        )}

                        {form.authority && (
                          <div className="small mt-1">
                            Authority:{" "}
                            {form.authority}
                          </div>
                        )}

                        {form.description && (
                          <p className="small mt-2">
                            {form.description}
                          </p>
                        )}

                        <button
                          type="button"
                          className="btn btn-primary mt-2"
                          onClick={() =>
                            handleSelectForm(form)
                          }
                        >
                          Select Form
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {!loading &&
              hasSearched &&
              results.length === 0 &&
              !error && (
                <div className="alert alert-info">
                  No matching forms found.
                </div>
              )}
          </div>

          {!session && (
            <form
              className="d-flex gap-2 mt-3"
              onSubmit={(e) => {
                e.preventDefault();
                handleSearch();
              }}
            >
              <input
                ref={inputRef}
                type="text"
                className="chat-input flex-grow-1"
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
              />

              <button
                className="send-btn"
                type="submit"
                disabled={loading}
              >
                ↑
              </button>
            </form>
          )}
        </main>

        <aside
          className="side-rail border-start p-3"
          style={{ width: 200 }}
        >
          <button
            type="button"
            className="side-item border-0 bg-transparent p-0 mb-3"
            onClick={focusSearch}
          >
            🔍 Search
          </button>

          <button
            type="button"
            className="side-item border-0 bg-transparent p-0"
            onClick={() => {
              console.log(
                "Quick links clicked"
              );
            }}
          >
            Quick links
          </button>
        </aside>
      </div>

      <footer className="app-footer p-2 text-center">
        Footer
      </footer>
    </div>
  );
}