import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogIn, Mail, Lock, AlertCircle, Sparkles } from "lucide-react";
import { apiFetch } from "../utils/api";

interface LoginPageProps {
  onLoginSuccess: (token: string, user: any) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        json: { email, password },
      });

      // Save tokens
      localStorage.setItem("token", data.access_token);
      
      // Fetch user profile info
      const userProfile = await apiFetch("/auth/me", { method: "GET" });
      localStorage.setItem("user", JSON.stringify(userProfile));
      
      onLoginSuccess(data.access_token, userProfile);
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-fade-in">
        {/* Title / Logo */}
        <div style={styles.header}>
          <div style={styles.logoCircle}>
            <Sparkles size={28} color="#fff" />
          </div>
          <h2 style={styles.title}>Welcome Back</h2>
          <p style={styles.subtitle}>Sign in to your AI Job Recommendation Assistant</p>
        </div>

        {/* Error Callout */}
        {error && (
          <div style={styles.errorBox}>
            <AlertCircle size={20} color="#ef4444" />
            <span style={styles.errorText}>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div style={styles.inputContainer}>
              <Mail size={18} color="#6b7280" style={styles.inputIcon} />
              <input
                type="email"
                required
                className="form-input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={styles.inputField}
              />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: "2rem" }}>
            <label className="form-label">Password</label>
            <div style={styles.inputContainer}>
              <Lock size={18} color="#6b7280" style={styles.inputIcon} />
              <input
                type="password"
                required
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={styles.inputField}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: "100%", padding: "0.85rem" }}
          >
            {loading ? "Signing in..." : "Sign In"}
            {!loading && <LogIn size={18} />}
          </button>
        </form>

        {/* Redirect Register link */}
        <div style={styles.footer}>
          <span>Don't have an account? </span>
          <Link to="/register" style={styles.link}>
            Sign up now
          </Link>
        </div>
      </div>
    </div>
  );
};

const styles = {
  header: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    textAlign: "center" as const,
    marginBottom: "2rem",
  },
  logoCircle: {
    width: "56px",
    height: "56px",
    borderRadius: "14px",
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "1.25rem",
    boxShadow: "0 10px 15px -3px rgba(99, 102, 241, 0.4)",
  },
  title: {
    fontSize: "1.75rem",
    fontWeight: 700,
    color: "#fff",
    marginBottom: "0.5rem",
  },
  subtitle: {
    fontSize: "0.9rem",
    color: "#9ca3af",
  },
  errorBox: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.85rem 1rem",
    backgroundColor: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    borderRadius: "8px",
    marginBottom: "1.5rem",
  },
  errorText: {
    fontSize: "0.85rem",
    color: "#fca5a5",
    fontWeight: 500,
  },
  inputContainer: {
    position: "relative" as const,
    display: "flex",
    alignItems: "center",
  },
  inputIcon: {
    position: "absolute" as const,
    left: "12px",
  },
  inputField: {
    paddingLeft: "2.5rem",
  },
  footer: {
    marginTop: "2rem",
    textAlign: "center" as const,
    fontSize: "0.875rem",
    color: "#9ca3af",
  },
  link: {
    color: "#6366f1",
    fontWeight: 600,
  },
};
export default LoginPage;
