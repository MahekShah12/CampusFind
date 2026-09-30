import React, { useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, User, ArrowRight } from "lucide-react";
import { useApp } from "../context/AppContext";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { handoverStatusLabel } from "../components/handover";

// Admin claim management: every claim, filterable, each opens the review page.
const AdminClaims = () => {
  const { adminClaims } = useApp();
  const [filter, setFilter] = useState("ALL");

  const count = (s) => adminClaims.filter((c) => c.status === s).length;
  const shown = adminClaims.filter((c) => filter === "ALL" || c.status === filter);

  return (
    <div className="container" style={{ padding: "2.5rem 1.5rem 4rem" }}>
      <div className="page-header" style={{ borderBottom: "none", paddingBottom: "0.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h1 className="page-title">Claim Management</h1>
            <p className="page-subtitle">All ownership claims submitted by students.</p>
          </div>
          <div className="type-toggle-group">
            {[
              ["ALL", `All (${adminClaims.length})`],
              ["PENDING", `Pending (${count("PENDING")})`],
              ["APPROVED", `Approved (${count("APPROVED")})`],
              ["REJECTED", `Rejected (${count("REJECTED")})`]
            ].map(([key, label]) => (
              <button
                key={key}
                className={`type-toggle-btn ${filter === key ? "active" : ""}`}
                onClick={() => setFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {shown.length === 0 ? (
        <EmptyState icon="inbox" title="No claims here." description="Nothing matches this filter yet." />
      ) : (
        <div className="claims-list">
          {shown.map((claim) => (
            <div key={claim.id} className="claim-card" style={{ alignItems: "center" }}>
              <div className="claim-card-content">
                <div className="claim-card-top">
                  <div>
                    <h3 className="claim-item-name">{claim.item_name}</h3>
                    <div className="claim-user-info">
                      <span>
                        <MapPin size={14} /> {claim.item_location}
                      </span>
                      <span>
                        <User size={14} /> {claim.claimant_name}
                      </span>
                      <span>{claim.date_claimed}</span>
                    </div>
                  </div>
                  <StatusBadge status={claim.status} />
                </div>
                {claim.status === "APPROVED" && (
                  <div style={{ fontSize: "0.85rem", color: "#166534", margin: "0.4rem 0" }}>
                    Handover: {claim.handover_location || "—"} · {handoverStatusLabel(claim.handover_status)}
                  </div>
                )}
                <div className="claim-actions">
                  <Link
                    to={`/admin/claims/${claim.id}`}
                    className="btn btn-secondary"
                    style={{ marginLeft: "auto", fontSize: "0.85rem", padding: "0.5rem 0.85rem" }}
                  >
                    <span>{claim.status === "PENDING" ? "Review Claim" : "Open"}</span>
                    <ArrowRight size={14} />
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

export default AdminClaims;
