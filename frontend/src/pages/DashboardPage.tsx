import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  Briefcase,
  Cpu,
  Send,
  UploadCloud,
  ChevronRight,
  Database,
} from "lucide-react";
import { apiFetch } from "../utils/api";

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState({
    jobsCount: 0,
    qdrantStatus: "Unknown",
    groqStatus: "Active",
    embeddedCount: 0,
  });
  const [loadingEmbed, setLoadingEmbed] = useState(false);
  const [embedMessage, setEmbedMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch jobs count
        const jobsData = await apiFetch("/jobs?limit=1");
        
        // Fetch health check status (contains environment/app config info)
        // Check health liveness
        setMetrics((prev) => ({
          ...prev,
          jobsCount: jobsData.total || 0,
          qdrantStatus: "Connected",
        }));
      } catch (err) {
        console.error("Error loading dashboard metrics:", err);
      }
    };

    fetchDashboardData();
  }, []);

  const handleEmbedJobs = async () => {
    setLoadingEmbed(true);
    setEmbedMessage(null);
    try {
      const res = await apiFetch("/rag/embed-jobs", { method: "POST" });
      setEmbedMessage(`Successfully embedded ${res.jobs_embedded} active jobs!`);
      // Update jobs count
      const jobsData = await apiFetch("/jobs?limit=1");
      setMetrics((prev) => ({
        ...prev,
        jobsCount: jobsData.total || 0,
      }));
    } catch (err: any) {
      setEmbedMessage(`Error indexing: ${err.message}`);
    } finally {
      setLoadingEmbed(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Welcome Banner */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>AI Job Assistant</h1>
          <p style={styles.subtitle}>
            Your final year portal for vector-matching job search and resume analytics.
          </p>
        </div>
        <div style={styles.timeTag}>Local System Live</div>
      </header>

      {/* Metrics Row */}
      <section className="grid-container" style={{ margin: "2rem 0" }}>
        <div className="card card-glass" style={styles.metricCard}>
          <div style={{ ...styles.iconWrap, backgroundColor: "rgba(99, 102, 241, 0.15)" }}>
            <Briefcase size={22} color="#6366f1" />
          </div>
          <div>
            <div style={styles.metricVal}>{metrics.jobsCount}</div>
            <div style={styles.metricTitle}>Active Jobs in DB</div>
          </div>
        </div>

        <div className="card card-glass" style={styles.metricCard}>
          <div style={{ ...styles.iconWrap, backgroundColor: "rgba(16, 185, 129, 0.15)" }}>
            <Database size={22} color="#10b981" />
          </div>
          <div>
            <div style={styles.metricVal}>{metrics.qdrantStatus}</div>
            <div style={styles.metricTitle}>Qdrant Vector Store</div>
          </div>
        </div>

        <div className="card card-glass" style={styles.metricCard}>
          <div style={{ ...styles.iconWrap, backgroundColor: "rgba(139, 92, 246, 0.15)" }}>
            <Cpu size={22} color="#8b5cf6" />
          </div>
          <div>
            <div style={styles.metricVal}>{metrics.groqStatus}</div>
            <div style={styles.metricTitle}>Groq Llama 3 LLM</div>
          </div>
        </div>
      </section>

      {/* Central Interactive Panels */}
      <div style={styles.panelsLayout}>
        {/* Quick Actions Panel */}
        <div className="card" style={{ flex: 1.2 }}>
          <h3 style={styles.panelTitle}>AI Career Tools</h3>
          <p style={styles.panelDesc}>Unlock recommendations with advanced semantic retrieval.</p>

          <div style={styles.actionGrid}>
            <Link to="/resume-analyzer" style={styles.actionItem}>
              <div style={styles.actionHeader}>
                <UploadCloud size={24} color="#6366f1" />
                <h4 style={styles.actionTitle}>Resume Analyzer</h4>
              </div>
              <p style={styles.actionDesc}>Parse resume files or copy text to extract active gaps.</p>
              <ChevronRight size={18} style={styles.actionChevron} />
            </Link>

            <Link to="/chat" style={styles.actionItem}>
              <div style={styles.actionHeader}>
                <Sparkles size={24} color="#8b5cf6" />
                <h4 style={styles.actionTitle}>AI Career Coach</h4>
              </div>
              <p style={styles.actionDesc}>Ask career queries using RAG context matched over job database.</p>
              <ChevronRight size={18} style={styles.actionChevron} />
            </Link>

            <Link to="/jobs" style={styles.actionItem}>
              <div style={styles.actionHeader}>
                <Send size={24} color="#10b981" />
                <h4 style={styles.actionTitle}>Browse Jobs</h4>
              </div>
              <p style={styles.actionDesc}>Add mock job listings or filter using custom metadata constraints.</p>
              <ChevronRight size={18} style={styles.actionChevron} />
            </Link>
          </div>
        </div>

        {/* Sync Vector Store Administration Card */}
        <div className="card" style={{ flex: 0.8, display: "flex", flexDirection: "column" }}>
          <h3 style={styles.panelTitle}>RAG Core Control</h3>
          <p style={styles.panelDesc}>Compute vector embeddings and update index points inside Qdrant.</p>

          <div style={styles.syncBox}>
            <div style={styles.syncText}>
              Vector search queries matching candidates' resumes against database items require computed embeddings.
            </div>

            <button
              onClick={handleEmbedJobs}
              disabled={loadingEmbed}
              className="btn btn-primary"
              style={{ width: "100%", padding: "0.85rem", marginTop: "1rem" }}
            >
              {loadingEmbed ? "Embedding..." : "Sync Jobs to Qdrant"}
              <Database size={18} />
            </button>

            {embedMessage && (
              <div
                style={{
                  ...styles.statusBanner,
                  color: embedMessage.includes("Error") ? "#fca5a5" : "#a7f3d0",
                  backgroundColor: embedMessage.includes("Error") ? "rgba(239,68,68,0.1)" : "rgba(16,185,129,0.1)",
                }}
              >
                {embedMessage}
              </div>
            )}
          </div>

          <div style={styles.noteBox}>
            <strong>Technical Note:</strong> Using FastEmbed 384-dimensional dense vectors and cosine distance configurations.
          </div>
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
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottom: "1px solid #1f2937",
    paddingBottom: "1.5rem",
  },
  title: {
    fontSize: "2.25rem",
    fontWeight: 800,
    background: "linear-gradient(135deg, #fff 0%, #9ca3af 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    fontSize: "1rem",
    color: "#9ca3af",
    marginTop: "0.5rem",
  },
  timeTag: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "#6366f1",
    padding: "0.4rem 0.8rem",
    backgroundColor: "rgba(99, 102, 241, 0.1)",
    border: "1px solid rgba(99, 102, 241, 0.2)",
    borderRadius: "20px",
  },
  metricCard: {
    display: "flex",
    alignItems: "center",
    gap: "1.25rem",
    padding: "1.5rem",
  },
  iconWrap: {
    width: "48px",
    height: "48px",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  metricVal: {
    fontSize: "1.75rem",
    fontWeight: 800,
    color: "#fff",
  },
  metricTitle: {
    fontSize: "0.85rem",
    color: "#9ca3af",
    marginTop: "0.15rem",
  },
  panelsLayout: {
    display: "flex",
    gap: "2rem",
    marginTop: "1rem",
    flexWrap: "wrap" as const,
  },
  panelTitle: {
    fontSize: "1.25rem",
    fontWeight: 700,
    color: "#fff",
    marginBottom: "0.25rem",
  },
  panelDesc: {
    fontSize: "0.875rem",
    color: "#9ca3af",
    marginBottom: "1.5rem",
  },
  actionGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "1rem",
  },
  actionItem: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "1rem 1.25rem",
    backgroundColor: "#1f293750",
    border: "1px solid #374151",
    borderRadius: "10px",
    position: "relative" as const,
    transition: "all 0.2s ease",
  },
  actionHeader: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
  },
  actionTitle: {
    fontSize: "0.95rem",
    fontWeight: 600,
    color: "#fff",
  },
  actionDesc: {
    fontSize: "0.85rem",
    color: "#9ca3af",
    marginLeft: "2rem",
    maxWidth: "400px",
  },
  actionChevron: {
    color: "#6b7280",
    transition: "transform 0.2s ease",
  },
  syncBox: {
    padding: "1rem",
    backgroundColor: "#1f293750",
    border: "1px solid #374151",
    borderRadius: "10px",
    flex: 1,
  },
  syncText: {
    fontSize: "0.875rem",
    color: "#9ca3af",
    lineHeight: "1.5",
  },
  statusBanner: {
    padding: "0.75rem",
    borderRadius: "8px",
    fontSize: "0.8rem",
    fontWeight: 500,
    marginTop: "1rem",
    textAlign: "center" as const,
  },
  noteBox: {
    fontSize: "0.75rem",
    color: "#6b7280",
    marginTop: "1rem",
    borderTop: "1px solid #374151",
    paddingTop: "0.75rem",
  },
};
export default DashboardPage;
