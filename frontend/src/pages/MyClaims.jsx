import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { MapPin, Calendar, CheckCircle2, ArrowRight, Lock } from "lucide-react";
import { useApp } from "../context/AppContext";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { handoverStatusLabel, FALLBACK_IMG } from "../components/handover";

// Student view: ONLY the claims the logged-in student submitted.
// No approve / reject / admin controls here.
const MyClaims = () => {
  const { myClaims } = useApp();
  const navigate = useNavigate();

  return (
    <div className="container" style={{ padding: "2.5rem 1.5rem 4rem" }}>
      <div className="page-header" style={{ borderBottom: "none", paddingBottom: "0.5rem" }}>
        <h1 className="page-title">My Claims</h1>
        <p className="page-subtitle">
          Track the ownership claims you submitted. Only campus admins can approve a claim.
        </p>
      </div>

      {myClaims.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="You haven't submitted any claims yet."
          description="Open a found item and tap “This is mine” to submit a claim."
          actionText="Browse Found Items"
          onAction={() => navigate("/")}
        />
      ) : (
        <div className="claims-list">
          {myClaims.map((claim) => (
            <div key={claim.id} className="claim-card">
              {claim.item_image ? (
                <img
                  src={claim.item_image}
                  alt={claim.item_name}
                  className="claim-item-thumb"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = FALLBACK_IMG;
                  }}
                />
              ) : (
                <div
                  className="claim-item-thumb"
                  style={{ display: "flex", alignItems: "center", justifyContent: "center", background: "#f1f5f9", color: "#94a3b8" }}
                  title="Image hidden for privacy"
                >
                  <Lock size={24} />
                </div>
              )}

              <div className="claim-card-content">
                <div className="claim-card-top">
                  <div>
                    <h3 className="claim-item-name">{claim.item_name}</h3>
                    <div className="claim-user-info">
                      <span>
                        <MapPin size={14} /> Found at {claim.item_location}
                      </span>
                      <span>
                        <Calendar size={14} /> Claimed on {claim.date_claimed}
                      </span>
                    </div>
                  </div>
                  <StatusBadge status={claim.status} />
                </div>

                <div className="claim-detail-box">
                  <div className="claim-detail-box-label">Your verification detail:</div>
                  <p className="claim-detail-text">"{claim.claim_detail}"</p>
                </div>

                <div style={{ margin: "0.75rem 0", fontWeight: 600 }}>
                  Claim Status: {claim.status}
                  {claim.status === "APPROVED" && " ✓"}
                </div>

                {claim.status === "PENDING" && (
                  <p style={{ color: "#64748b", fontSize: "0.9rem" }}>
                    Waiting for an admin to verify your claim.
                  </p>
                )}

                {claim.status === "APPROVED" && (
                  <div
                    style={{
                      background: "#f0fdf4",
                      border: "1px solid #bbf7d0",
                      borderRadius: 10,
                      padding: "0.85rem 1rem",
                      color: "#166534",
                      fontSize: "0.9rem"
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 700 }}>
                      <CheckCircle2 size={16} /> Claim Approved ✓
                    </div>
                    {claim.handover_location ? (
                      <>
                        <div style={{ marginTop: "0.5rem" }}>
                          <strong>Handover Location:</strong> {claim.handover_location}
                        </div>
                        <div>
                          <strong>Status:</strong> {handoverStatusLabel(claim.handover_status)}
                        </div>
                        {claim.handover_status !== "COMPLETED" && (
                          <p style={{ marginTop: "0.4rem" }}>
                            Please collect your item from the designated location.
                          </p>
                        )}
                      </>
                    ) : (
                      <p style={{ marginTop: "0.4rem" }}>An admin will assign a safe handover location soon.</p>
                    )}
                  </div>
                )}

                {claim.status === "REJECTED" && (
                  <p style={{ color: "#dc2626", fontSize: "0.9rem", fontWeight: 600 }}>
                    Claim Status: REJECTED
                  </p>
                )}

                <div className="claim-actions">
                  <Link
                    to={`/items/${claim.item_id}`}
                    className="btn btn-secondary"
                    style={{ marginLeft: "auto", fontSize: "0.85rem", padding: "0.5rem 0.85rem" }}
                  >
                    <span>View Item</span>
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

export default MyClaims;
