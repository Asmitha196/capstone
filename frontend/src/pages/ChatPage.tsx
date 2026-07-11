import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Briefcase, User } from "lucide-react";
import { apiFetch } from "../utils/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  contextJobs?: any[];
}

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your AI Career Coach. Ask me anything about our database of job postings or seek career advice, and I will search relevant positions to answer contextually.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      // Call RAG Ask endpoint
      const data = await apiFetch("/rag/ask", {
        method: "POST",
        json: {
          question: userMessage,
        },
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          contextJobs: data.context_jobs,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry, I encountered an error answering your question: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={styles.logoWrap}>
            <Sparkles size={22} color="#fff" />
          </div>
          <div>
            <h1 style={styles.title}>AI Career Coach</h1>
            <p style={styles.subtitle}>
              Conversational QA driven by Retrieval-Augmented Generation (RAG) context.
            </p>
          </div>
        </div>
      </header>

      {/* Main Chat Layout */}
      <div style={styles.chatArea}>
        {/* Chat Messages Logs */}
        <div style={styles.messageBox}>
          {messages.map((msg, idx) => {
            const isAI = msg.role === "assistant";
            return (
              <div key={idx} style={{ ...styles.messageRow, justifyContent: isAI ? "flex-start" : "flex-end" }}>
                {isAI && (
                  <div style={{ ...styles.avatarCircle, backgroundColor: "#8b5cf6" }}>
                    <Sparkles size={16} />
                  </div>
                )}
                
                <div style={styles.messageWrapper}>
                  <div
                    style={{
                      ...styles.bubble,
                      backgroundColor: isAI ? "#1f2937" : "#6366f1",
                      border: isAI ? "1px solid #374151" : "none",
                      color: "#fff",
                    }}
                  >
                    <p style={styles.messageText}>{msg.content}</p>
                  </div>

                  {/* Render Contextual Jobs if returned */}
                  {isAI && msg.contextJobs && msg.contextJobs.length > 0 && (
                    <div style={styles.contextJobsBox}>
                      <div style={styles.contextHeader}>
                        <Briefcase size={14} color="#6366f1" />
                        <span>Retrieved Context Listings:</span>
                      </div>
                      <div style={styles.jobsGrid}>
                        {msg.contextJobs.map((job) => (
                          <div key={job.id} style={styles.jobBadge}>
                            <div style={styles.jobTitle}>{job.title}</div>
                            <div style={styles.jobCompany}>
                              {job.company} · {job.location || "Remote"}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {!isAI && (
                  <div style={{ ...styles.avatarCircle, backgroundColor: "#374151" }}>
                    <User size={16} />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div style={styles.messageRow}>
              <div style={{ ...styles.avatarCircle, backgroundColor: "#8b5cf6" }}>
                <Sparkles size={16} className="animate-spin" />
              </div>
              <div style={styles.bubbleLoading}>
                <div style={styles.loadingDot}></div>
                <div style={styles.loadingDot}></div>
                <div style={styles.loadingDot}></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar Form */}
        <form onSubmit={handleSend} style={styles.inputForm}>
          <input
            type="text"
            disabled={loading}
            className="form-input"
            placeholder="e.g. Do you have any Python backend positions matching PostgreSQL in San Francisco?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={styles.chatInput}
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn btn-primary" style={styles.sendBtn}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1000px",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column" as const,
    height: "calc(100vh - 5rem)",
  },
  header: {
    borderBottom: "1px solid #1f2937",
    paddingBottom: "1rem",
    marginBottom: "1rem",
  },
  logoWrap: {
    width: "44px",
    height: "44px",
    borderRadius: "10px",
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: "1.75rem",
    fontWeight: 800,
    color: "#fff",
  },
  subtitle: {
    fontSize: "0.9rem",
    color: "#9ca3af",
    marginTop: "0.15rem",
  },
  chatArea: {
    flex: 1,
    display: "flex",
    flexDirection: "column" as const,
    backgroundColor: "#111827",
    border: "1px solid #374151",
    borderRadius: "16px",
    overflow: "hidden",
  },
  messageBox: {
    flex: 1,
    padding: "2rem",
    overflowY: "auto" as const,
    display: "flex",
    flexDirection: "column" as const,
    gap: "1.5rem",
  },
  messageRow: {
    display: "flex",
    gap: "1rem",
    alignItems: "flex-start",
    maxWidth: "85%",
  },
  avatarCircle: {
    width: "36px",
    height: "36px",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    flexShrink: 0,
    boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
  },
  messageWrapper: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "0.5rem",
  },
  bubble: {
    padding: "1rem 1.25rem",
    borderRadius: "14px",
    lineHeight: "1.5",
    fontSize: "0.95rem",
  },
  messageText: {
    whiteSpace: "pre-line" as const,
  },
  contextJobsBox: {
    marginTop: "0.5rem",
    padding: "0.85rem 1rem",
    backgroundColor: "#1f293780",
    border: "1px solid #374151",
    borderRadius: "10px",
  },
  contextHeader: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontSize: "0.8rem",
    fontWeight: 700,
    color: "#6366f1",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    marginBottom: "0.5rem",
  },
  jobsGrid: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "0.5rem",
  },
  jobBadge: {
    backgroundColor: "#111827",
    border: "1px solid #374151",
    borderRadius: "6px",
    padding: "0.4rem 0.6rem",
    fontSize: "0.75rem",
    maxWidth: "200px",
  },
  jobTitle: {
    fontWeight: 600,
    color: "#fff",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap" as const,
  },
  jobCompany: {
    color: "#9ca3af",
    fontSize: "0.7rem",
    marginTop: "0.1rem",
  },
  inputForm: {
    display: "flex",
    gap: "0.75rem",
    padding: "1.25rem 2rem",
    borderTop: "1px solid #374151",
    backgroundColor: "#0b0f19",
  },
  chatInput: {
    flex: 1,
    backgroundColor: "#1f2937",
    border: "1px solid #374151",
    padding: "0.85rem 1.25rem",
  },
  sendBtn: {
    padding: "0.85rem",
    flexShrink: 0,
  },
  bubbleLoading: {
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
    padding: "1rem 1.5rem",
    borderRadius: "14px",
    backgroundColor: "#1f2937",
    border: "1px solid #374151",
    width: "70px",
    justifyContent: "center",
  },
  loadingDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    backgroundColor: "#9ca3af",
    animation: "bounce 1.4s infinite ease-in-out both",
  },
};
export default ChatPage;
