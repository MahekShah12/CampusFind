import React, { useState } from "react";
import { X, ShieldCheck, AlertCircle, CheckCircle2 } from "lucide-react";
import { useApp } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";

const ClaimModal = ({ item, isOpen, onClose }) => {
  const { addClaim } = useApp();
  const { user } = useAuth();
  const [claimantName, setClaimantName] = useState(user?.name || "");
  const [claimantEmail, setClaimantEmail] = useState(user?.email || "");
  const [claimantPhone, setClaimantPhone] = useState("");
  const [claimDetail, setClaimDetail] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedSuccess, setSubmittedSuccess] = useState(false);

  if (!isOpen || !item) return null;

  const validate = () => {
    const errs = {};
    if (!claimantName.trim()) {
      errs.claimantName = "Your name or Student ID is required.";
    }
    if (!claimantEmail.trim()) {
      errs.claimantEmail = "Campus email is required for the finder to contact you.";
    }
    if (!claimDetail.trim()) {
      errs.claimDetail = "Please provide verification details that only the true owner would know.";
    } else if (claimDetail.trim().length < 8) {
      errs.claimDetail = "Please provide a more descriptive detail (at least 8 characters).";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const [submitError, setSubmitError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setSubmitError("");

    // POST /api/claims
    const claimPayload = {
      item_id: item.id,
      claimant_name: claimantName.trim(),
      claimant_email: claimantEmail.trim(),
      claimant_phone: claimantPhone.trim(),
      claim_detail: claimDetail.trim(),
    };

    try {
      await addClaim(claimPayload);
      setSubmittedSuccess(true);
    } catch (err) {
      console.error("Failed to submit claim", err);
      setSubmitError(
        err?.response?.data?.detail || "Could not submit your claim. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setSubmittedSuccess(false);
    setClaimDetail("");
    setClaimantName("");
    setClaimantEmail("");
    setClaimantPhone("");
    setErrors({});
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <ShieldCheck size={24} style={{ color: "#2563eb" }} />
            <h3 className="modal-title">Claim This Item</h3>
          </div>
          <button className="modal-close-btn" onClick={handleClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        {submittedSuccess ? (
          <div style={{ textAlign: "center", padding: "1.5rem 0" }}>
            <div
              style={{
                width: 60,
                height: 60,
                borderRadius: "50%",
                background: "#d1fae5",
                color: "#059669",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 1.25rem",
              }}
            >
              <CheckCircle2 size={36} />
            </div>
            <h4 style={{ fontSize: "1.3rem", fontWeight: 800, marginBottom: "0.5rem" }}>
              Claim Submitted Successfully!
            </h4>
            <p style={{ color: "#64748b", fontSize: "0.95rem", marginBottom: "1.5rem" }}>
              An admin will verify your details. You can track the status under <strong>My Claims</strong>.
            </p>
            <button className="btn btn-primary" onClick={handleClose}>
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="modal-explanation-box">
              <p>
                Claiming: <strong>{item.item_name}</strong> (Found at {item.location})
              </p>
              <p style={{ marginTop: "0.3rem", fontSize: "0.82rem" }}>
                Help us verify that this item belongs to you. Enter private details that only the true owner would know.
              </p>
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label className="form-label">
                  Your Full Name / Student ID <span className="required">*</span>
                </label>
                <input
                  type="text"
                  className={`form-input ${errors.claimantName ? "input-error" : ""}`}
                  placeholder="e.g. Rahul Sharma (Roll 2024CS042)"
                  value={claimantName}
                  onChange={(e) => setClaimantName(e.target.value)}
                />
                {errors.claimantName && (
                  <div className="form-error-msg">
                    <AlertCircle size={14} />
                    <span>{errors.claimantName}</span>
                  </div>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  Campus Email <span className="required">*</span>
                </label>
                <input
                  type="email"
                  className={`form-input ${errors.claimantEmail ? "input-error" : ""}`}
                  placeholder="name@campus.edu"
                  value={claimantEmail}
                  onChange={(e) => setClaimantEmail(e.target.value)}
                />
                {errors.claimantEmail && (
                  <div className="form-error-msg">
                    <AlertCircle size={14} />
                    <span>{errors.claimantEmail}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Private Verification Detail <span className="required">*</span>
              </label>
              <textarea
                rows={4}
                className={`form-textarea ${errors.claimDetail ? "input-error" : ""}`}
                placeholder="Enter a detail that proves ownership (e.g. A specific sticker on the back, unique scratch, wallpaper image, or what's inside the wallet/bag)."
                value={claimDetail}
                onChange={(e) => setClaimDetail(e.target.value)}
              />
              <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.3rem" }}>
                Example: <em>"There is a small Harry Potter sticker on the inner bottom case."</em>
              </div>
              {errors.claimDetail && (
                <div className="form-error-msg">
                  <AlertCircle size={14} />
                  <span>{errors.claimDetail}</span>
                </div>
              )}
            </div>

            {submitError && (
              <div className="form-error-msg" style={{ marginBottom: "0.75rem" }}>
                <AlertCircle size={14} />
                <span>{submitError}</span>
              </div>
            )}

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={handleClose}>
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit Claim"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ClaimModal;
