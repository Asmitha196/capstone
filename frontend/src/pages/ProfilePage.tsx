import React, { useState, useEffect } from "react";
import { User, Mail, MapPin, Briefcase, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { apiFetch } from "../utils/api";

interface ProfilePageProps {
  onProfileUpdate: (updatedUser: any) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onProfileUpdate }) => {
  const [profile, setProfile] = useState({
    email: "",
    full_name: "",
    headline: "",
    location: "",
    years_of_experience: 0,
    bio: "",
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await apiFetch("/auth/me");
        setProfile({
          email: data.email || "",
          full_name: data.full_name || "",
          headline: data.headline || "",
          location: data.location || "",
          years_of_experience: data.years_of_experience || 0,
          bio: data.bio || "",
        });
      } catch (err) {
        console.error("Error loading user profile:", err);
      }
    };
    loadProfile();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(null);
    setError(null);

    try {
      const payload = {
        full_name: profile.full_name,
        headline: profile.headline,
        location: profile.location,
        years_of_experience: Number(profile.years_of_experience),
        bio: profile.bio,
      };

      const updatedData = await apiFetch("/auth/me", {
        method: "PUT",
        json: payload,
      });

      // Update local storage
      localStorage.setItem("user", JSON.stringify(updatedData));
      
      // Update global parent states
      onProfileUpdate(updatedData);
      setSuccess("Profile settings updated successfully!");
    } catch (err: any) {
      setError(err.message || "Failed to update profile settings.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Candidate Profile</h1>
          <p style={styles.subtitle}>Manage your professional background details and credentials.</p>
        </div>
      </header>

      <div style={styles.layout}>
        {/* Profile Form Card */}
        <div className="card" style={{ flex: 1.2 }}>
          <h3 style={styles.sectionTitle}>Profile Details</h3>
          <p style={styles.sectionDesc}>This information is used to compute ATS match scores and target gaps.</p>

          {success && (
            <div style={styles.successBox}>
              <CheckCircle size={18} color="#10b981" />
              <span>{success}</span>
            </div>
          )}

          {error && (
            <div style={styles.errorBox}>
              <AlertCircle size={18} color="#ef4444" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSave}>
            <div style={styles.formRow}>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Full Name</label>
                <div style={styles.inputContainer}>
                  <User size={16} color="#6b7280" style={styles.inputIcon} />
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    style={styles.inputField}
                  />
                </div>
              </div>

              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Email Address (Read-only)</label>
                <div style={styles.inputContainer}>
                  <Mail size={16} color="#6b7280" style={styles.inputIcon} />
                  <input
                    type="email"
                    disabled
                    className="form-input"
                    value={profile.email}
                    style={{ ...styles.inputField, backgroundColor: "#1f293750", cursor: "not-allowed" }}
                  />
                </div>
              </div>
            </div>

            <div style={styles.formRow}>
              <div className="form-group" style={{ flex: 1.2 }}>
                <label className="form-label">Headline / Job Title</label>
                <div style={styles.inputContainer}>
                  <Briefcase size={16} color="#6b7280" style={styles.inputIcon} />
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Senior Software Engineer"
                    value={profile.headline}
                    onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
                    style={styles.inputField}
                  />
                </div>
              </div>

              <div className="form-group" style={{ flex: 0.8 }}>
                <label className="form-label">Years of Experience</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  value={profile.years_of_experience}
                  onChange={(e) => setProfile({ ...profile, years_of_experience: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Location</label>
              <div style={styles.inputContainer}>
                <MapPin size={16} color="#6b7280" style={styles.inputIcon} />
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. San Francisco, CA or Remote"
                  value={profile.location}
                  onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                  style={styles.inputField}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Professional Biography</label>
              <textarea
                className="form-input"
                placeholder="Write a brief professional summary describing your core stack and expertise..."
                rows={5}
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                style={{ resize: "vertical" }}
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: "100%", padding: "0.85rem", marginTop: "1rem" }}>
              {loading ? "Saving Changes..." : "Save Profile Settings"}
            </button>
          </form>
        </div>

        {/* Info Box Card */}
        <div style={{ flex: 0.8, display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="card card-glass" style={styles.infoCard}>
            <div style={styles.avatarBig}>
              {profile.full_name.charAt(0).toUpperCase() || "C"}
            </div>
            <h3 style={styles.infoName}>{profile.full_name || "Candidate"}</h3>
            <p style={styles.infoHeadline}>{profile.headline || "Job Seeker"}</p>
            <p style={styles.infoLoc}>{profile.location || "Remote"}</p>
          </div>

          <div className="card" style={{ flex: 1 }}>
            <h4 style={styles.cardHeader}>Why fill profile metrics?</h4>
            <ul style={styles.helpList}>
              <li style={styles.helpItem}>
                <FileText size={16} color="#6366f1" style={{ flexShrink: 0, marginTop: "0.15rem" }} />
                <span>Provides a semantic baseline target matching context during ATS calculations.</span>
              </li>
              <li style={styles.helpItem}>
                <Briefcase size={16} color="#8b5cf6" style={{ flexShrink: 0, marginTop: "0.15rem" }} />
                <span>Fine-tunes the AI coach response parameters context matched against active listings.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1100px",
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
  formRow: {
    display: "flex",
    gap: "1.5rem",
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
  infoCard: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    textAlign: "center" as const,
    padding: "2rem",
    backgroundColor: "#111827",
  },
  avatarBig: {
    width: "80px",
    height: "80px",
    borderRadius: "50%",
    backgroundColor: "#6366f1",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: "2rem",
    color: "#fff",
    marginBottom: "1rem",
    boxShadow: "0 10px 15px -3px rgba(99,102,241,0.3)",
  },
  infoName: {
    fontSize: "1.25rem",
    fontWeight: 700,
    color: "#fff",
  },
  infoHeadline: {
    fontSize: "0.85rem",
    color: "#9ca3af",
    marginTop: "0.25rem",
  },
  infoLoc: {
    fontSize: "0.8rem",
    color: "#6b7280",
    marginTop: "0.5rem",
  },
  cardHeader: {
    fontSize: "0.95rem",
    fontWeight: 700,
    color: "#fff",
    marginBottom: "1rem",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
  },
  helpList: {
    listStyleType: "none",
    display: "flex",
    flexDirection: "column" as const,
    gap: "1rem",
  },
  helpItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.75rem",
    fontSize: "0.875rem",
    color: "#cbd5e1",
    lineHeight: "1.4",
  },
  successBox: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.85rem 1rem",
    backgroundColor: "rgba(16, 185, 129, 0.1)",
    border: "1px solid rgba(16, 185, 129, 0.2)",
    borderRadius: "8px",
    color: "#a7f3d0",
    fontSize: "0.85rem",
    marginBottom: "1.5rem",
    fontWeight: 500,
  },
  errorBox: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
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
export default ProfilePage;
