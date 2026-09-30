import React, { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { ShieldAlert } from "lucide-react";
import { useAuth } from "../context/AuthContext";

// Frontend route guard. (The backend enforces the same rules independently.)
//   role="ADMIN"   -> admins only. A student sees "Access Denied" then goes Home.
//   role="STUDENT" -> students only. An admin is sent to the admin dashboard.
//   no role        -> any logged-in user.
const RequireRole = ({ role, children }) => {
  const { user } = useAuth();
  const location = useLocation();
  const [redirect, setRedirect] = useState(false);

  const denied = !!user && role === "ADMIN" && user.role !== "ADMIN";

  useEffect(() => {
    if (!denied) return undefined;
    setRedirect(false);
    const t = setTimeout(() => setRedirect(true), 2500);
    return () => clearTimeout(t);
  }, [denied, location.pathname]);

  if (!user) return <Navigate to="/login" replace />;

  if (role === "STUDENT" && user.role === "ADMIN") {
    return <Navigate to="/admin" replace />;
  }

  if (denied) {
    if (redirect) return <Navigate to="/" replace />;
    return (
      <div className="container" style={{ padding: "5rem 1.5rem", textAlign: "center" }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            background: "#fee2e2",
            color: "#dc2626",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 1.25rem"
          }}
        >
          <ShieldAlert size={34} />
        </div>
        <h1 className="page-title" style={{ marginBottom: "0.4rem" }}>Access Denied</h1>
        <p className="page-subtitle">Admin privileges are required.</p>
        <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginTop: "0.75rem" }}>
          Redirecting you to the home page…
        </p>
      </div>
    );
  }

  return children;
};

export default RequireRole;
