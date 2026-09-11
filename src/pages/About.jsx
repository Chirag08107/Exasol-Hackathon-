import Navbar from "../components/Navbar";
import { Link } from "react-router-dom";

const FEATURES = [
  {
    icon: "🧭",
    title: "Guided, step by step",
    desc: "Plain-language checklists for each of 80+ Indian government forms — no more guessing which field means what.",
  },
  {
    icon: "📎",
    title: "Know what to bring",
    desc: "Every form lists the exact supporting documents you need, sourced from official government guidance.",
  },
  {
    icon: "⚠️",
    title: "Avoid common mistakes",
    desc: "We flag the errors that most often get applications rejected or delayed, before you submit.",
  },
  {
    icon: "🔒",
    title: "Your data, protected",
    desc: "Verification details are used only to confirm your identity and are never shared without consent.",
  },
];

const STATS = [
  { figure: "80+", caption: "government forms covered" },
  { figure: "6", caption: "categories — tax, identity, banking & more" },
  { figure: "800+", caption: "field-level validation rules" },
];

export default function About() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />
      <main className="flex-grow-1">
        <section className="text-center py-5 px-3">
          <span className="hero-eyebrow">About FormSahay</span>
          <h1 className="hero-title">
            Built to make Indian<br /><span className="accent-word">government paperwork painless.</span>
          </h1>
          <p className="hero-subtitle">
            FormSahay is a hackathon project for the Exasol Hackathon — an AI assistant that
            turns confusing government forms into a clear, guided conversation. This is the
            frontend draft; the Exasol-backed reasoning engine is coming next.
          </p>
        </section>

        <section className="container py-4">
          <div className="row g-3 text-center justify-content-center mb-5">
            {STATS.map((s) => (
              <div className="col-6 col-md-3" key={s.caption}>
                <div className="stat-figure">{s.figure}</div>
                <div className="stat-caption">{s.caption}</div>
              </div>
            ))}
          </div>

          <div className="section-label text-center">Why FormSahay</div>
          <div className="row g-3">
            {FEATURES.map((f) => (
              <div className="col-md-6" key={f.title}>
                <div className="feature-card">
                  <div className="feature-card-icon">{f.icon}</div>
                  <h3 style={{ fontSize: "1.1rem" }}>{f.title}</h3>
                  <p style={{ color: "var(--ink-soft)", marginBottom: 0 }}>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="text-center py-5">
          <h2 className="mb-3">Ready to try it?</h2>
          <Link to="/signup" className="btn-brand me-2">Create an account</Link>
          <Link to="/" className="btn-brand-outline">Open the assistant</Link>
        </section>
      </main>
      <footer className="app-footer p-2 text-center">
        © {new Date().getFullYear()} FormSahay — Built for the Exasol Hackathon
      </footer>
    </div>
  );
}
