import React, { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  MapPin,
  Calendar,
  ArrowLeft,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Mail,
  User,
  AlertCircle,
  Phone,
  Lock,
  Image as ImageIcon
} from "lucide-react";
import { useApp } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";
import StatusBadge from "../components/StatusBadge";
import ClaimModal from "../components/ClaimModal";
import EmptyState from "../components/EmptyState";

const ItemDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getItemById } = useApp();
  const { isAdmin } = useAuth();

  const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const item = getItemById(id);

  if (!item) {
    return (
      <div className="container" style={{ padding: "4rem 1.5rem" }}>
        <EmptyState
          icon="error"
          title="Item Not Found"
          description="The item you are looking for does not exist or may have been removed."
          actionText="Back to All Items"
          onAction={() => navigate("/")}
        />
      </div>
    );
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    try {
      const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
      return new Date(dateStr).toLocaleDateString("en-US", options);
    } catch {
      return dateStr;
    }
  };

  const isFound = item.type === "FOUND";
  const isRecovered = item.status === "RECOVERED";
  const isClaimed = item.status === "CLAIMED";
  const isPrivate = item.image_visibility === "PRIVATE";
  const isNone = item.image_visibility === "NONE" || (!item.image_url && !isPrivate);

  return (
    <div className="container" style={{ padding: "2rem 1.5rem 4rem" }}>
      {/* Back Link */}
      <Link to="/" className="back-link">
        <ArrowLeft size={16} />
        <span>Back to Items</span>
      </Link>

      <div className="item-details-layout">
        {/* Left: Image Panel with Privacy Support */}
        <div className="details-image-panel">
          <div className="details-image-wrapper">
            {isPrivate ? (
              <div className="details-image-private-box">
                <div className="private-shield-icon">
                  <Lock size={44} />
                </div>
                <h3 className="private-box-title">
                  🔒 Image hidden for privacy
                </h3>
                <p className="private-box-subtitle">
                  This image is only available for verification.
                </p>
              </div>
            ) : isNone ? (
              <div className="details-image-none-box">
                <ImageIcon size={48} className="none-box-icon" />
                <h3 className="none-box-title">No image provided</h3>
                <p className="none-box-subtitle">
                  No photograph was uploaded for this item.
                </p>
              </div>
            ) : (
              <img
                src={item.image_url}
                alt={item.item_name}
                className="details-image"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src =
                    "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?auto=format&fit=crop&w=800&q=80";
                }}
              />
            )}
          </div>

          {/* Read-only lifecycle status (only admins can change it, via claim review) */}
          <div
            style={{
              marginTop: "1rem",
              padding: "0.75rem 1rem",
              backgroundColor: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "10px",
              fontSize: "0.85rem",
              color: "#64748b",
            }}
          >
            Lifecycle Status: <strong style={{ color: "#0f172a" }}>{item.status}</strong>
          </div>
        </div>

        {/* Right: Details and Claim Actions */}
        <div className="details-info-panel">
          <div className="details-header-badges">
            <StatusBadge type={item.type} />
            <StatusBadge status={item.status} />
            {isPrivate && (
              <span className="status-badge" style={{ backgroundColor: "#fef3c7", color: "#92400e", border: "1px solid #fde68a" }}>
                <Lock size={12} /> PRIVATE IMAGE
              </span>
            )}
          </div>

          <h1 className="details-title">{item.item_name}</h1>
          <span className="details-category-pill">{item.category}</span>

          <div className="details-metadata-grid">
            <div className="meta-box">
              <span className="meta-box-label">Campus Location</span>
              <div className="meta-box-value">
                <MapPin size={16} style={{ color: "#ef4444" }} />
                <span>{item.location}</span>
              </div>
            </div>

            <div className="meta-box">
              <span className="meta-box-label">Date {item.type === "FOUND" ? "Found" : "Lost"}</span>
              <div className="meta-box-value">
                <Calendar size={16} style={{ color: "#2563eb" }} />
                <span>{formatDate(item.date_reported)}</span>
              </div>
            </div>

            {item.reported_by && (
              <div className="meta-box">
                <span className="meta-box-label">Reported By</span>
                <div className="meta-box-value">
                  <User size={16} style={{ color: "#64748b" }} />
                  <span>{item.reported_by}</span>
                </div>
              </div>
            )}

            {item.contact_email && (
              <div className="meta-box">
                <span className="meta-box-label">Official Campus Contact</span>
                <div className="meta-box-value">
                  <Mail size={16} style={{ color: "#64748b" }} />
                  <span>{item.contact_email}</span>
                </div>
              </div>
            )}
          </div>

          {/* Phone numbers are never shown publicly. Contact happens through the
              admin-verified claim + safe handover flow. */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.75rem 1rem",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: 10,
              fontSize: "0.85rem",
              color: "#475569",
              marginBottom: "1rem",
            }}
          >
            <Lock size={14} />
            Contact details are private. Ownership is verified by campus admins and items are handed over at a safe campus location.
          </div>

          <h3 className="details-desc-title">Public Description</h3>
          <p className="details-description">{item.description}</p>

          {/* CRITICAL NOTE: private_detail is NEVER rendered on this public page! */}

          {/* Ownership Claim Action Callout */}
          {isAdmin ? (
            <div className="claim-cta-box">
              <div className="claim-cta-text">
                <h4>Admin view</h4>
                <p>Review claims for this item from Claim Management.</p>
              </div>
            </div>
          ) : item.is_mine ? (
            <div className="claim-cta-box">
              <div className="claim-cta-text">
                <h4>You reported this item</h4>
                <p>You can track it under My Reports.</p>
              </div>
            </div>
          ) : isFound ? (
            <div className="claim-cta-box">
              <div className="claim-cta-text">
                <h4>Is this your item?</h4>
                <p>
                  {isRecovered
                    ? "This item has already been verified and recovered by its owner."
                    : isClaimed
                    ? "An ownership claim is currently being verified for this item."
                    : "Submit a claim with private verification details known only to you."}
                </p>
              </div>

              <button
                onClick={() => setIsClaimModalOpen(true)}
                className="btn btn-primary btn-lg"
                disabled={isRecovered || isClaimed}
                style={{
                  opacity: isRecovered || isClaimed ? 0.6 : 1,
                  cursor: isRecovered || isClaimed ? "not-allowed" : "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                <ShieldCheck size={18} />
                This is Mine
              </button>
            </div>
          ) : (
            <div
              style={{
                backgroundColor: "#fffbeb",
                border: "1px solid #fde68a",
                borderRadius: "12px",
                padding: "1.25rem",
                marginTop: "auto",
              }}
            >
              <h4 style={{ color: "#92400e", fontWeight: 700, fontSize: "1rem", marginBottom: "0.25rem" }}>
                Found this lost item?
              </h4>
              <p style={{ color: "#78350f", fontSize: "0.88rem", marginBottom: "0.75rem" }}>
                If you have spotted or recovered this belonging, please report it so we can reconnect it with the student.
              </p>
              <button
                onClick={() => navigate("/report?type=FOUND")}
                className="btn btn-warning"
              >
                Report as Found Item
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Claim Modal */}
      <ClaimModal
        item={item}
        isOpen={isClaimModalOpen}
        onClose={() => setIsClaimModalOpen(false)}
      />

      {/* Floating feedback toast */}
      {toastMessage && (
        <div className="toast-notice">
          <CheckCircle size={18} style={{ color: "#10b981" }} />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
};

export default ItemDetails;
