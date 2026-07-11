import React, { useState } from "react";
import { UploadCloud, FileText, AlertTriangle, Lightbulb, UserCheck, Play } from "lucide-react";
import { apiFetch } from "../utils/api";

export const ResumePage: React.FC = () => {
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Results state
  const [analysis, setAnalysis] = useState<{
    extracted_skills: string[];
    experience: string;
    missing_skills: string[];
    recommendations: string[];
  } | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeText.trim() || resumeText.trim().length < 50) {
      setError("Please paste a comprehensive resume containing at least 50 characters.");
      return;
    }
    
    setError(null);
    setLoading(true);

    try {
      // Trigger RAG-based resume analysis
      const data = await apiFetch("/rag/analyse-resume", {
        method: "POST",
        json: {
          resume_text: resumeText,
        },
      });

      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze resume.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Resume Analyzer</h1>
          <p style={styles.subtitle}>
            Extract skills, parse experience, and align gaps using contextual database matching.
          </p>
        </div>
      </header>

      <div style={styles.layout}>
        {/* Input Box */}
        <div className="card" style={styles.inputCard}>
          <h3 style={styles.sectionTitle}>Paste Resume Content</h3>
          <p style={styles.sectionDesc}>Paste the plain text of your resume to compare against database requirements.</p>

          {error && <div style={styles.errorBox}>{error}</div>}

          <form onSubmit={handleAnalyze}>
            <div className="form-group">
              <textarea
                required
                className="form-input"
                placeholder="Paste work history, skills matrix, summary, and certifications here..."
                rows={16}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                style={styles.textarea}
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: "100%", padding: "0.85rem" }}>
              {loading ? "Parsing & Analyzing..." : "Run AI Resume Scan"}
              <Play size={16} />
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div style={styles.resultsPanel}>
          {analysis ? (
            <div style={styles.resultsGrid}>
              {/* Experience Summary */}
              <div className="card" style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <UserCheck size={20} color="#10b981" />
                  <h4 style={styles.resultTitle}>Experience Summary</h4>
                </div>
                <p style={styles.experienceText}>{analysis.experience}</p>
              </div>

              {/* Extracted Skills */}
              <div className="card" style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <FileText size={20} color="#6366f1" />
                  <h4 style={styles.resultTitle}>Identified Competencies</h4>
                </div>
                <div style={styles.pillContainer}>
                  {analysis.extracted_skills.map((skill) => (
                    <span key={skill} className="badge badge-success" style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="card" style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <AlertTriangle size={20} color="#f59e0b" />
                  <h4 style={styles.resultTitle}>Skills & Credentials Gaps</h4>
                </div>
                <p style={{ fontSize: "0.85rem", color: "#9ca3af", marginBottom: "0.75rem" }}>
                  These elements were found in matching job descriptions but are missing in your resume.
                </p>
                <div style={styles.pillContainer}>
                  {analysis.missing_skills.map((skill) => (
                    <span key={skill} className="badge badge-danger" style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actionable Recommendations */}
              <div className="card" style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <Lightbulb size={20} color="#8b5cf6" />
                  <h4 style={styles.resultTitle}>Optimization Recommendations</h4>
                </div>
                <ul style={styles.recList}>
                  {analysis.recommendations.map((rec, i) => (
                    <li key={i} style={styles.recItem}>
                      <span style={styles.recBullet}>{i + 1}</span>
                      <span style={styles.recText}>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div style={styles.noResultsBox}>
              <UploadCloud size={48} color="#374151" />
              <h4>Awaiting Input</h4>
              <p>Submit your resume text. Our LLM pipeline will parse metrics and cross-compare gaps against active job postings.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
  },
  header: {
    borderBottom: "1px solid #1f2937",
    paddingBottom: "1.5rem",
    marginBottom: "2rem",
  },
  title: {
    fontSize: "2.25rem",
    fontWeight: 800,
    color: "#fff",
  },
  subtitle: {
    fontSize: "1rem",
    color: "#9ca3af",
    marginTop: "0.25rem",
  },
  layout: {
    display: "flex",
    gap: "2rem",
    flexWrap: "wrap" as const,
  },
  inputCard: {
    flex: 1,
    minWidth: "320px",
    backgroundColor: "#111827",
  },
  sectionTitle: {
    fontSize: "1.25rem",
    fontWeight: 700,
    color: "#fff",
    marginBottom: "0.25rem",
  },
  sectionDesc: {
    fontSize: "0.875rem",
    color: "#9ca3af",
    marginBottom: "1.5rem",
  },
  textarea: {
    fontFamily: "monospace",
    fontSize: "0.85rem",
    resize: "vertical" as const,
    backgroundColor: "#0b0f19",
  },
  resultsPanel: {
    flex: 1.2,
    minWidth: "360px",
  },
  resultsGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "1.5rem",
  },
  resultCard: {
    backgroundColor: "#111827",
  },
  resultHeader: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    borderBottom: "1px solid #374151",
    paddingBottom: "0.75rem",
    marginBottom: "1rem",
  },
  resultTitle: {
    fontSize: "1rem",
    fontWeight: 700,
    color: "#fff",
  },
  experienceText: {
    fontSize: "0.95rem",
    color: "#cbd5e1",
    lineHeight: "1.6",
  },
  pillContainer: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "0.5rem",
  },
  recList: {
    listStyleType: "none",
    display: "flex",
    flexDirection: "column" as const,
    gap: "1rem",
  },
  recItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.85rem",
  },
  recBullet: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "22px",
    height: "22px",
    borderRadius: "50%",
    backgroundColor: "rgba(139, 92, 246, 0.15)",
    color: "#8b5cf6",
    fontSize: "0.75rem",
    fontWeight: 700,
    flexShrink: 0,
  },
  recText: {
    fontSize: "0.9rem",
    color: "#cbd5e1",
    lineHeight: "1.4",
  },
  noResultsBox: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center" as const,
    padding: "6rem 2rem",
    border: "1px dashed #374151",
    borderRadius: "12px",
    color: "#9ca3af",
    gap: "1rem",
    backgroundColor: "#11182750",
  },
  errorBox: {
    padding: "0.85rem 1rem",
    backgroundColor: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    borderRadius: "8px",
    color: "#fca5a5",
    fontSize: "0.85rem",
    marginBottom: "1.5rem",
    fontWeight: 500,
  },
};
export default ResumePage;
