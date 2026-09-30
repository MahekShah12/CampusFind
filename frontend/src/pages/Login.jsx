import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { Search, User, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getDemoUsers } from "../services/api";

// Demo-only login: choose a seeded user to demonstrate role permissions.
const Login = () => {
  const { user, login } = useAuth();
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  useEffect(() => {
    getDemoUsers()
      .then((res) => setUsers(res.data))
      .catch(() =>
        setError("Could not reach the backend. Start it at http://127.0.0.1:8000 and refresh.")
      );
  }, []);

  if (user) return <Navigate to={user.role === "ADMIN" ? "/admin" : "/"} replace />;

  const handleLogin = async (email) => {
    setBusy(email);
    setError("");
    try {
      await login(email);
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setBusy("");
    }
  };

  const students = users.filter((u) => u.role === "STUDENT");
  const admins = users.filter((u) => u.role === "ADMIN");

  const UserButton = ({ u }) => (
    <button
      type="button"
      className={`btn ${u.role === "ADMIN" ? "btn-primary" : "btn-secondary"}`}
      style={{ width: "100%", justifyContent: "flex-start", gap: "0.6rem", marginBottom: "0.6rem" }}
      disabled={!!busy}
      onClick={() => handleLogin(u.email)}
    >
      {u.role === "ADMIN" ? <ShieldCheck size={16} /> : <User size={16} />}
      <span>{busy === u.email ? "Signing in…" : u.name}</span>
      <span style={{ marginLeft: "auto", fontSize: "0.75rem", opacity: 0.7 }}>{u.email}</span>
    </button>
  );

  return (
    <div className="container" style={{ padding: "4rem 1.5rem", maxWidth: 520 }}>
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <div className="brand-logo-icon" style={{ margin: "0 auto 1rem" }}>
          <Search size={22} strokeWidth={2.5} />
        </div>
        <h1 className="page-title">
          Campus<span style={{ color: "#2563eb" }}>Find</span>
        </h1>
        <p className="page-subtitle">Demo login — choose who you want to be.</p>
      </div>

      {error && (
        <div className="form-error-msg" style={{ marginBottom: "1rem" }}>
          <span>{error}</span>
        </div>
      )}

      <div className="claim-card" style={{ flexDirection: "column", alignItems: "stretch" }}>
        <div className="form-label" style={{ marginBottom: "0.5rem" }}>Login as Student</div>
        {students.map((u) => (
          <UserButton key={u.id} u={u} />
        ))}
        <div className="form-label" style={{ margin: "0.75rem 0 0.5rem" }}>Login as Admin</div>
        {admins.map((u) => (
          <UserButton key={u.id} u={u} />
        ))}
        <p style={{ fontSize: "0.78rem", color: "#94a3b8", marginTop: "0.75rem" }}>
          Demo mode only — no passwords. The backend still enforces student/admin permissions on every request.
        </p>
      </div>
    </div>
  );
};

export default Login;
