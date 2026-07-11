import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  MessageSquare,
  User,
  LogOut,
  Sparkles,
} from "lucide-react";

interface SidebarProps {
  user: any;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Browse Jobs", path: "/jobs", icon: Briefcase },
    { name: "Resume Analyzer", path: "/resume-analyzer", icon: FileText },
    { name: "AI Career Chat", path: "/chat", icon: MessageSquare },
    { name: "Profile", path: "/profile", icon: User },
  ];

  return (
    <aside style={styles.sidebar}>
      {/* Brand Header */}
      <div style={styles.brand}>
        <Sparkles size={24} color="#6366f1" />
        <span style={styles.brandText}>JobAssistant AI</span>
      </div>

      {/* User Info Capsule */}
      <div style={styles.userCapsule}>
        <div style={styles.avatar}>
          {user?.full_name?.charAt(0).toUpperCase() || "U"}
        </div>
        <div style={styles.userInfo}>
          <div style={styles.userName}>{user?.full_name || "User Profile"}</div>
          <div style={styles.userRole}>{user?.headline || "Job Seeker"}</div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={styles.nav}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.path}
              style={{
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              }}
            >
              <Icon size={20} color={isActive ? "#fff" : "#9ca3af"} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Logout Footer Button */}
      <button onClick={onLogout} style={styles.logoutBtn}>
        <LogOut size={20} />
        <span>Sign Out</span>
      </button>
    </aside>
  );
};

const styles = {
  sidebar: {
    width: "280px",
    backgroundColor: "#111827",
    borderRight: "1px solid #374151",
    padding: "2rem 1.5rem",
    display: "flex",
    flexDirection: "column" as const,
    height: "100vh",
    position: "sticky" as const,
    top: 0,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    marginBottom: "2.5rem",
  },
  brandText: {
    fontSize: "1.25rem",
    fontWeight: 700,
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  userCapsule: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "1rem",
    backgroundColor: "#1f2937",
    border: "1px solid #374151",
    borderRadius: "12px",
    marginBottom: "2rem",
  },
  avatar: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    backgroundColor: "#6366f1",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: "1.1rem",
    color: "#fff",
    flexShrink: 0,
  },
  userInfo: {
    overflow: "hidden",
  },
  userName: {
    fontSize: "0.9rem",
    fontWeight: 600,
    color: "#fff",
    whiteSpace: "nowrap" as const,
    overflow: "hidden",
    textOverflow: "ellipsis",
  },
  userRole: {
    fontSize: "0.75rem",
    color: "#9ca3af",
    whiteSpace: "nowrap" as const,
    overflow: "hidden",
    textOverflow: "ellipsis",
  },
  nav: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "0.5rem",
    flex: 1,
  },
  navLink: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    padding: "0.75rem 1rem",
    borderRadius: "8px",
    color: "#9ca3af",
    fontWeight: 500,
    fontSize: "0.95rem",
    transition: "all 0.2s ease",
  },
  navLinkActive: {
    backgroundColor: "#6366f1",
    color: "#fff",
    fontWeight: 600,
  },
  logoutBtn: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    padding: "0.75rem 1rem",
    borderRadius: "8px",
    backgroundColor: "transparent",
    border: "1px solid #ef444450",
    color: "#ef4444",
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.2s ease",
    marginTop: "auto",
  },
};
export default Sidebar;
