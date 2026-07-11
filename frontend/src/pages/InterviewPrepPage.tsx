import React, { useState } from "react";
import {
  Brain,
  Code2,
  MessageCircle,
  Link2,
  ChevronDown,
  ChevronUp,
  Play,
  BookOpen,
  Target,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";
import { apiFetch } from "../utils/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface PracticeLinks {
  aptitude: string[];
  technical: string[];
  communication: string[];
}

interface PrepItem {
  job_id: string;
  job_title: string;
  company: string;
  match_score: number;
  missing_skills: string[];
  aptitude_topics: string[];
  technical_topics: string[];
  communication_topics: string[];
  practice_links: PracticeLinks;
}

// ── Score ring helper ─────────────────────────────────────────────────────────

const ScoreRing: React.FC<{ score: number }> = ({ score }) => {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color =
    score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div style={styles.scoreRingWrap}>
      <svg width="72" height="72">
        <circle cx="36" cy="36" r={r} fill="none" stroke="#1f2937" strokeWidth="5" />
        <circle
          cx="36" cy="36" r={r}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 36 36)"
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
        <text x="36" y="41" textAnchor="middle" fill={color} fontSize="13" fontWeight="700">
          {Math.round(score)}%
        </text>
      </svg>
    </div>
  );
};

// ── Topic pill ────────────────────────────────────────────────────────────────

const Pill: React.FC<{ label: string; color: string; bg: string }> = ({ label, color, bg }) => (
  <span style={{ ...styles.pill, color, backgroundColor: bg }}>{label}</span>
);

// ── Link row ──────────────────────────────────────────────────────────────────

const ResourceLink: React.FC<{ url: string }> = ({ url }) => {
  const label = url.replace(/^https?:\/\/(www\.)?/, "").split("/")[0];
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" style={styles.resourceLink}>
      <ExternalLink size={13} />
      {label}
    </a>
  );
};

// ── Prep Section box ──────────────────────────────────────────────────────────

const PrepSection: React.FC<{
  icon: React.ReactNode;
  title: string;
  accentColor: string;
  children: React.ReactNode;
}> = ({ icon, title, accentColor, children }) => (
  <div style={{ ...styles.prepBox, borderColor: `${accentColor}33` }}>
    <div style={{ ...styles.prepBoxHeader, color: accentColor }}>
      {icon}
      <span style={styles.prepBoxTitle}>{title}</span>
    </div>
    {children}
  </div>
);

// ── Single Job Prep Card ───────────────────────────────────────────────────────

const JobPrepCard: React.FC<{ item: PrepItem; rank: number }> = ({ item, rank }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={styles.jobCard}>
      {/* Card header */}
      <div style={styles.cardHeader}>
        <div style={styles.cardHeaderLeft}>
          <span style={styles.rankBadge}>#{rank}</span>
          <div>
            <h3 style={styles.jobTitle}>{item.job_title}</h3>
            <p style={styles.companyName}>{item.company}</p>
          </div>
        </div>
        <div style={styles.cardHeaderRight}>
          <ScoreRing score={item.match_score} />
        </div>
      </div>

      {/* Missing skills */}
      {item.missing_skills.length > 0 && (
        <div style={styles.missingSkillsRow}>
          <AlertTriangle size={14} color="#f59e0b" style={{ flexShrink: 0, marginTop: "1px" }} />
          <span style={styles.missingLabel}>Skill Gaps:</span>
          <div style={styles.pillRow}>
            {item.missing_skills.slice(0, 6).map((s) => (
              <Pill key={s} label={s} color="#f59e0b" bg="rgba(245,158,11,0.12)" />
            ))}
            {item.missing_skills.length > 6 && (
              <span style={styles.moreTag}>+{item.missing_skills.length - 6} more</span>
            )}
          </div>
        </div>
      )}

      {/* Expand button */}
      <button
        style={styles.prepButton}
        onClick={() => setExpanded((v) => !v)}
      >
        <Target size={15} />
        {expanded ? "Hide Interview Prep" : "Prepare for Interview"}
        {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>

      {/* Expandable panel */}
      {expanded && (
        <div style={styles.expandPanel}>
          <div style={styles.prepGrid}>
            {/* Aptitude */}
            <PrepSection icon={<Brain size={16} />} title="Aptitude Preparation" accentColor="#6366f1">
              <div style={styles.pillRow}>
                {item.aptitude_topics.map((t) => (
                  <Pill key={t} label={t} color="#818cf8" bg="rgba(99,102,241,0.12)" />
                ))}
              </div>
            </PrepSection>

            {/* Technical */}
            <PrepSection icon={<Code2 size={16} />} title="Technical Preparation" accentColor="#10b981">
              <div style={styles.pillRow}>
                {item.technical_topics.map((t) => {
                  const isMissing = item.missing_skills
                    .map((s) => s.toLowerCase())
                    .includes(t.toLowerCase());
                  return (
                    <Pill
                      key={t}
                      label={t}
                      color={isMissing ? "#ef4444" : "#34d399"}
                      bg={isMissing ? "rgba(239,68,68,0.12)" : "rgba(16,185,129,0.12)"}
                    />
                  );
                })}
              </div>
              {item.missing_skills.length > 0 && (
                <p style={styles.hintText}>
                  <span style={{ color: "#ef4444" }}>■</span> Red = missing from your resume
                </p>
              )}
            </PrepSection>

            {/* Communication */}
            <PrepSection icon={<MessageCircle size={16} />} title="Communication Preparation" accentColor="#8b5cf6">
              <div style={styles.pillRow}>
                {item.communication_topics.map((t) => (
                  <Pill key={t} label={t} color="#a78bfa" bg="rgba(139,92,246,0.12)" />
                ))}
              </div>
            </PrepSection>

            {/* Practice Links */}
            <PrepSection icon={<Link2 size={16} />} title="Practice Resources" accentColor="#06b6d4">
              <div style={styles.linksGrid}>
                <div>
                  <p style={styles.linkGroupLabel}>📐 Aptitude</p>
                  {item.practice_links.aptitude.map((url) => (
                    <ResourceLink key={url} url={url} />
                  ))}
                </div>
                <div>
                  <p style={styles.linkGroupLabel}>💻 Technical</p>
                  {item.practice_links.technical.map((url) => (
                    <ResourceLink key={url} url={url} />
                  ))}
                </div>
                <div>
                  <p style={styles.linkGroupLabel}>🗣️ Communication</p>
                  {item.practice_links.communication.map((url) => (
                    <ResourceLink key={url} url={url} />
                  ))}
                </div>
              </div>
            </PrepSection>
          </div>
        </div>
      )}
    </div>
  );
};

// ── Main Page ─────────────────────────────────────────────────────────────────

export const InterviewPrepPage: React.FC = () => {
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<PrepItem[] | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (resumeText.trim().length < 50) {
      setError("Please paste a resume with at least 50 characters.");
      return;
    }
    setError(null);
    setLoading(true);
    setItems(null);

    try {
      const data = await apiFetch("/interview-prep/recommendations", {
        method: "POST",
        json: { resume_text: resumeText },
      });
      setItems(data.items || []);
    } catch (err: any) {
      setError(err.message || "Failed to generate interview prep.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.pageTitle}>Interview Preparation</h1>
          <p style={styles.pageSubtitle}>
            Paste your resume to get personalized interview prep cards for your top 5 matched jobs.
          </p>
        </div>
      </header>

      <div style={styles.layout}>
        {/* Input Panel */}
        <div className="card" style={styles.inputCard}>
          <div style={styles.inputCardHeader}>
            <BookOpen size={20} color="#6366f1" />
            <h3 style={styles.sectionTitle}>Your Resume</h3>
          </div>
          <p style={styles.sectionDesc}>
            Paste the plain text of your resume. We'll match it against live job listings and
            generate tailored interview prep for each.
          </p>

          {error && <div style={styles.errorBox}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <textarea
                required
                className="form-input"
                placeholder="Paste your resume text here — skills, experience, education, projects..."
                rows={18}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                style={styles.textarea}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: "100%", padding: "0.9rem" }}
            >
              {loading ? "Matching jobs & generating prep..." : "Generate Interview Prep"}
              <Play size={15} />
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div style={styles.resultsPanel}>
          {loading && (
            <div style={styles.loadingBox}>
              <div style={styles.spinner} />
              <p style={{ color: "#9ca3af", marginTop: "1rem" }}>
                Matching resume against jobs and building your prep cards...
              </p>
            </div>
          )}

          {!loading && items === null && (
            <div style={styles.emptyBox}>
              <Target size={48} color="#374151" />
              <h4 style={{ color: "#9ca3af", marginTop: "1rem" }}>Awaiting Resume</h4>
              <p style={{ color: "#6b7280", fontSize: "0.875rem", marginTop: "0.5rem", maxWidth: "280px" }}>
                Submit your resume to get interview preparation cards for your best-matching positions.
              </p>
            </div>
          )}

          {!loading && items && items.length === 0 && (
            <div style={styles.emptyBox}>
              <AlertTriangle size={40} color="#f59e0b" />
              <h4 style={{ color: "#f59e0b", marginTop: "1rem" }}>No Jobs Found</h4>
              <p style={{ color: "#9ca3af", fontSize: "0.875rem", marginTop: "0.5rem" }}>
                No matching job listings found. Ask your admin to add and embed jobs first.
              </p>
            </div>
          )}

          {!loading && items && items.length > 0 && (
            <div style={styles.cardList}>
              <p style={styles.resultCount}>
                Showing prep for <strong style={{ color: "#6366f1" }}>{items.length}</strong> top matched job{items.length !== 1 ? "s" : ""}
              </p>
              {items.map((item, i) => (
                <JobPrepCard key={item.job_id} item={item} rank={i + 1} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: { maxWidth: "1300px", margin: "0 auto" },
  header: {
    borderBottom: "1px solid #1f2937",
    paddingBottom: "1.5rem",
    marginBottom: "2rem",
  },
  pageTitle: { fontSize: "2.25rem", fontWeight: 800, color: "#fff" },
  pageSubtitle: { fontSize: "1rem", color: "#9ca3af", marginTop: "0.25rem" },

  layout: { display: "flex", gap: "2rem", flexWrap: "wrap" },
  inputCard: { flex: "0 0 360px", minWidth: "300px", backgroundColor: "#111827", alignSelf: "flex-start" },
  inputCardHeader: { display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.25rem" },
  sectionTitle: { fontSize: "1.15rem", fontWeight: 700, color: "#fff" },
  sectionDesc: { fontSize: "0.85rem", color: "#9ca3af", marginBottom: "1.25rem", lineHeight: "1.5" },
  textarea: { fontFamily: "monospace", fontSize: "0.82rem", resize: "vertical", backgroundColor: "#0b0f19" },
  errorBox: {
    padding: "0.85rem 1rem",
    backgroundColor: "rgba(239,68,68,0.1)",
    border: "1px solid rgba(239,68,68,0.2)",
    borderRadius: "8px",
    color: "#fca5a5",
    fontSize: "0.85rem",
    marginBottom: "1.25rem",
  },

  resultsPanel: { flex: 1, minWidth: "360px" },
  resultCount: { fontSize: "0.9rem", color: "#9ca3af", marginBottom: "1rem" },
  cardList: { display: "flex", flexDirection: "column", gap: "1.25rem" },

  loadingBox: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", padding: "5rem 2rem",
    border: "1px dashed #374151", borderRadius: "12px",
  },
  spinner: {
    width: "40px", height: "40px", borderRadius: "50%",
    border: "3px solid #1f2937", borderTopColor: "#6366f1",
    animation: "spin 1s linear infinite",
  },
  emptyBox: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", textAlign: "center", padding: "5rem 2rem",
    border: "1px dashed #374151", borderRadius: "12px", backgroundColor: "#11182750",
  },

  // Job Card
  jobCard: {
    background: "rgba(17,24,39,0.85)",
    backdropFilter: "blur(12px)",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: "14px",
    padding: "1.5rem",
    boxShadow: "0 4px 24px rgba(0,0,0,0.2)",
    transition: "border-color 0.2s ease",
  },
  cardHeader: {
    display: "flex", justifyContent: "space-between",
    alignItems: "flex-start", marginBottom: "1rem",
  },
  cardHeaderLeft: { display: "flex", alignItems: "flex-start", gap: "0.75rem" },
  cardHeaderRight: { flexShrink: 0 },
  rankBadge: {
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    width: "28px", height: "28px", borderRadius: "50%",
    background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
    color: "#fff", fontSize: "0.75rem", fontWeight: 700, flexShrink: 0, marginTop: "3px",
  },
  jobTitle: { fontSize: "1.1rem", fontWeight: 700, color: "#f9fafb" },
  companyName: { fontSize: "0.85rem", color: "#9ca3af", marginTop: "2px" },
  scoreRingWrap: {},

  missingSkillsRow: {
    display: "flex", alignItems: "flex-start", gap: "0.5rem",
    flexWrap: "wrap", marginBottom: "1rem",
    padding: "0.75rem", borderRadius: "8px",
    backgroundColor: "rgba(245,158,11,0.06)",
    border: "1px solid rgba(245,158,11,0.15)",
  },
  missingLabel: { fontSize: "0.8rem", color: "#9ca3af", fontWeight: 600, whiteSpace: "nowrap", marginTop: "2px" },
  moreTag: { fontSize: "0.75rem", color: "#6b7280", alignSelf: "center" },

  prepButton: {
    display: "flex", alignItems: "center", gap: "0.5rem",
    width: "100%", justifyContent: "center",
    padding: "0.7rem 1rem",
    background: "linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15))",
    border: "1px solid rgba(99,102,241,0.3)",
    borderRadius: "10px", color: "#a5b4fc", fontWeight: 600,
    fontSize: "0.875rem", cursor: "pointer",
    transition: "all 0.2s ease",
  },

  expandPanel: {
    marginTop: "1.25rem",
    borderTop: "1px solid rgba(255,255,255,0.06)",
    paddingTop: "1.25rem",
  },
  prepGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(260px,1fr))", gap: "1rem" },
  prepBox: {
    background: "rgba(11,15,25,0.6)",
    backdropFilter: "blur(8px)",
    border: "1px solid",
    borderRadius: "10px",
    padding: "1rem",
  },
  prepBoxHeader: {
    display: "flex", alignItems: "center", gap: "0.5rem",
    marginBottom: "0.75rem", fontWeight: 700, fontSize: "0.875rem",
  },
  prepBoxTitle: {},

  pillRow: { display: "flex", flexWrap: "wrap", gap: "0.4rem" },
  pill: {
    display: "inline-flex", alignItems: "center",
    padding: "0.25rem 0.65rem", borderRadius: "9999px",
    fontSize: "0.75rem", fontWeight: 600,
  },
  hintText: { fontSize: "0.72rem", color: "#6b7280", marginTop: "0.6rem" },

  linksGrid: { display: "flex", flexDirection: "column", gap: "0.75rem" },
  linkGroupLabel: { fontSize: "0.78rem", color: "#9ca3af", fontWeight: 600, marginBottom: "0.35rem" },
  resourceLink: {
    display: "flex", alignItems: "center", gap: "0.35rem",
    fontSize: "0.8rem", color: "#06b6d4", textDecoration: "none",
    marginBottom: "0.25rem", transition: "color 0.15s ease",
  },
};

export default InterviewPrepPage;
