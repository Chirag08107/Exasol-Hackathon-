import Navbar from "../components/Navbar";
import { useState } from "react";

export default function Landing() {
  const [message, setMessage] = useState("");

  return (
    <div className="d-flex flex-column vh-100">
      <Navbar />
      <div className="d-flex flex-grow-1">
        <aside className="side-rail border-end p-3" style={{ width: 220 }}>
          <button className="btn-brand-outline w-100 mb-3">+ New Chat</button>
          <div className="side-item">Option 1</div>
          <div className="side-item">Option 2</div>
          <div className="side-item">Option 3</div>
        </aside>

        <main className="flex-grow-1 d-flex flex-column p-4">
          <div className="flex-grow-1 d-flex align-items-center justify-content-center">
            <span className="chat-prompt">What's in your mind?</span>
          </div>
          <form
            className="d-flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setMessage("");
            }}
          >
            <input
              className="chat-input flex-grow-1"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message..."
            />
            <button className="send-btn">↑</button>
          </form>
        </main>

        <aside className="side-rail border-start p-3" style={{ width: 200 }}>
          <div className="side-item mb-2">🔍 Search</div>
          <div className="side-item">Quick links</div>
        </aside>
      </div>
      <footer className="app-footer p-2 text-center">Footer</footer>
    </div>
  );
}
