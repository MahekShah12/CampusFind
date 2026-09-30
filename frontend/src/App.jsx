import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AppProvider, useApp } from "./context/AppContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import RequireRole from "./components/RequireRole";
import Home from "./pages/Home";
import ReportItem from "./pages/ReportItem";
import ItemDetails from "./pages/ItemDetails";
import Login from "./pages/Login";
import MyClaims from "./pages/MyClaims";
import MyReports from "./pages/MyReports";
import AdminDashboard from "./pages/AdminDashboard";
import AdminClaims from "./pages/AdminClaims";
import AdminClaimReview from "./pages/AdminClaimReview";

const BackendStatusBanner = () => {
  const { isLoading, loadError, reload } = useApp();

  if (loadError) {
    return (
      <div
        style={{
          background: "#fef2f2",
          color: "#991b1b",
          borderBottom: "1px solid #fecaca",
          padding: "0.75rem 1.5rem",
          fontSize: "0.85rem",
          textAlign: "center",
        }}
      >
        {loadError}{" "}
        <button
          onClick={reload}
          style={{
            marginLeft: "0.5rem",
            background: "none",
            border: "none",
            color: "#991b1b",
            fontWeight: 700,
            textDecoration: "underline",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        style={{
          background: "#f8fafc",
          color: "#64748b",
          borderBottom: "1px solid #e2e8f0",
          padding: "0.6rem 1.5rem",
          fontSize: "0.85rem",
          textAlign: "center",
        }}
      >
        Loading CampusFind items…
      </div>
    );
  }

  return null;
};

// /claims used to be the generic claims page -> send each role to its own page.
const LegacyClaimsRedirect = () => {
  const { isAdmin } = useAuth();
  return <Navigate to={isAdmin ? "/admin/claims" : "/my-claims"} replace />;
};

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Router>
          <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
            <Navbar />
            <BackendStatusBanner />
            <main style={{ flexGrow: 1 }}>
              <Routes>
                <Route path="/login" element={<Login />} />

                {/* Any logged-in user */}
                <Route path="/" element={<RequireRole><Home /></RequireRole>} />
                <Route path="/items/:id" element={<RequireRole><ItemDetails /></RequireRole>} />
                <Route path="/claims" element={<RequireRole><LegacyClaimsRedirect /></RequireRole>} />

                {/* Student routes */}
                <Route path="/report" element={<RequireRole role="STUDENT"><ReportItem /></RequireRole>} />
                <Route path="/my-claims" element={<RequireRole role="STUDENT"><MyClaims /></RequireRole>} />
                <Route path="/my-reports" element={<RequireRole role="STUDENT"><MyReports /></RequireRole>} />

                {/* Admin routes */}
                <Route path="/admin" element={<RequireRole role="ADMIN"><AdminDashboard /></RequireRole>} />
                <Route path="/admin/claims" element={<RequireRole role="ADMIN"><AdminClaims /></RequireRole>} />
                <Route path="/admin/claims/:id" element={<RequireRole role="ADMIN"><AdminClaimReview /></RequireRole>} />

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </AppProvider>
    </AuthProvider>
  );
}

export default App;
