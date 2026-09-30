import React from "react";
import { Link } from "react-router-dom";
import { Package, Clock, CheckCircle2, Archive, MapPin, User } from "lucide-react";
import { useApp } from "../context/AppContext";
import EmptyState from "../components/EmptyState";

const StatCard = ({ label, value, icon, color }) => (
  <div className="admin-stat-card">
    <div className="admin-stat-icon" style={{ background: `${color}1a`, color }}>
      {icon}
    </div>
    <div>
      <div className="admin-stat-value">{value ?? "–"}</div>
      <div className="admin-stat-label">{label}</div>
    </div>
  </div>
);

const AdminDashboard = () => {
  const { adminClaims, adminStats } = useApp();
  const pending = adminClaims.filter((c) => c.status === "PENDING");

  return (
    <div className="container" style={{ padding: "2.5rem 1.5rem 4rem" }}>
      <div className="page-header" style={{ borderBottom: "none", paddingBottom: "0.5rem" }}>
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle">Verify ownership claims and manage safe item handovers.</p>
      </div>

      <div className="admin-stat-grid">
        <StatCard label="Total Items" value={adminStats?.total_items} icon={<Package size={20} />} color="#2563eb" />
        <StatCard label="Pending Claims" value={adminStats?.pending_claims} icon={<Clock size={20} />} color="#d97706" />
        <StatCard label="Approved Claims" value={adminStats?.approved_claims} icon={<CheckCircle2 size={20} />} color="#059669" />
        <StatCard label="Recovered Items" value={adminStats?.recovered_items} icon={<Archive size={20} />} color="#7c3aed" />
      </div>

      <h2 style={{ fontSize: "1.2rem", fontWeight: 800, margin: "2rem 0 1rem" }}>Pending Claims</h2>

      {pending.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="No pending claims."
          description="New ownership claims will appear here for review."
        />
      ) : (
        <div className="claims-list">
          {pending.map((claim) => (
            <div key={claim.id} className="claim-card" style={{ alignItems: "center" }}>
              <div className="claim-card-content">
                <h3 className="claim-item-name">{claim.item_name}</h3>
                <div className="claim-user-info">
                  <span>
                    <MapPin size={14} /> Found at: {claim.item_location}
                  </span>
                  <span>
                    <User size={14} /> Claimant: <strong style={{ color: "#0f172a" }}>{claim.claimant_name}</strong>
                  </span>
                  <span>Claim submitted: {claim.date_claimed}</span>
                </div>
                <div className="claim-actions">
                  <Link to={`/admin/claims/${claim.id}`} className="btn btn-primary">
                    Review Claim
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
