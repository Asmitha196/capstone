import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { JobsPage } from "./pages/JobsPage";
import { ResumePage } from "./pages/ResumePage";
import { ChatPage } from "./pages/ChatPage";
import { ProfilePage } from "./pages/ProfilePage";

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any>(null);
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    
    if (token && storedUser) {
      setIsAuthenticated(true);
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem("user");
      }
    }
    setCheckingAuth(false);
  }, []);

  const handleLoginSuccess = (_token: string, loggedInUser: any) => {
    setIsAuthenticated(true);
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
  };

  const handleProfileUpdate = (updatedUser: any) => {
    setUser(updatedUser);
  };

  if (checkingAuth) {
    return (
      <div style={styles.spinnerWrap}>
        <div style={styles.spinner}></div>
        <p style={{ marginTop: "1rem", color: "#9ca3af" }}>Loading Career Assistant...</p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      {isAuthenticated ? (
        <div className="app-container">
          <Sidebar user={user} onLogout={handleLogout} />
          <main className="main-content">
            <Routes>
              <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/resume-analyzer" element={<ResumePage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/profile" element={<ProfilePage onProfileUpdate={handleProfileUpdate} />} />
              </Route>
              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      ) : (
        <Routes>
          <Route path="/login" element={<LoginPage onLoginSuccess={handleLoginSuccess} />} />
          <Route path="/register" element={<RegisterPage />} />
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </BrowserRouter>
  );
};

const styles = {
  spinnerWrap: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    backgroundColor: "#0b0f19",
  },
  spinner: {
    width: "48px",
    height: "48px",
    borderRadius: "50%",
    border: "3px solid #1f2937",
    borderTopColor: "#6366f1",
    animation: "spin 1s linear infinite",
  },
};

export default App;
