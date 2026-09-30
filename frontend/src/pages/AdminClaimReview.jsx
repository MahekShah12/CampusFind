import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Check, X, Lock, CheckCircle2, ShieldCheck } from "lucide-react";
import { useApp } from "../context/AppContext";
import { getAdminClaim } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import { HANDOVER_LOCATIONS, handoverStatusLabel } from "../components/handover";

const box = { background: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "1.25rem", marginBottom: "1rem" };
const label = { fontSize: "0.72rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.04em" };
const row = { marginBottom: "0.6rem" };

// Admin-only claim review. Every action here is re-checked by the backend.
const AdminClaimReview = () => {
  const { id } = useParams();
  const { adminDecideClaim, adminUpdateHandover, adminMarkRecovered } = useApp();
  const [claim, setClaim] = useState(null);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const [location, setLocation] = useState(HANDOVER_LOCATIONS[0]);
  const [otherText, setOtherText] = useState("");

  useEffect(() => {
    getAdminClaim(id)
      .then((res) => {
        setClaim(res.data);
        const known = HANDOVER_LOCATIONS.includes(res.data.handover_location);
        if (known) setLocation(res.data.handover_location);
        else if (res.data.handover_location?.startsWith("Other:")) {
          setLocation("Other");
          setOtherText(res.data.handover_location.replace("Other:", "").trim());
        }
      })
      .catch((err) =>
        setError(err?.response?.status === 404 ? "Claim not found." : err?.response?.data?.detail || "Could not load claim.")
      );
  }, [id]);

  const chosenLocation = location === "Other" ? `Other: ${otherText.trim()}` : location;
  const locationInvalid = location === "Other" && !otherText.trim();

  const run = async (fn, okMsg) => {
    setBusy(true);
    setError("");
    try {
      const updated = await fn();
      // recovered endpoint returns a small object, so reload the full claim
      const fresh = await getAdminClaim(id);
      setClaim(fresh.data);
      void updated;
      setToast(okMsg);
      setTimeout(() => setToast(""), 3500);
    } catch (err) {
      setError(err?.response?.data?.detail || "Action failed.");
    } finally {
      setBusy(false);
    }
  };

  if (error && !claim) {
    return (
      <div className="container" style={{ padding: "3rem 1.5rem" }}>
        <p style={{ color: "#dc2626" }}>{error}</p>
        <Link to="/admin/claims" className="back-link"><ArrowLeft size={16} /> Back to claims</Link>
      </div>
    );
  }
  if (!claim) return <div className="container" style={{ padding: "3rem 1.5rem" }}>Loading claim…</div>;

  const isPending = claim.status === "PENDING";
  const isApproved = claim.status === "APPROVED";
  const completed = claim.handover_status === "COMPLETED";

  const LocationPicker = () => (
    <div style={{ marginBottom: "0.75rem" }}>
      <div style={label}>Handover Location</div>
      <select className="form-input" value={location} onChange={(e) => setLocation(e.target.value)} style={{ marginTop: "0.3rem" }}>
        {HANDOVER_LOCATIONS.map((l) => (
          <option key={l} value={l}>{l}</option>
        ))}
      </select>
      {location === "Other" && (
        <input
          className="form-input"
          style={{ marginTop: "0.5rem" }}
          placeholder="Name the college-approved location"
          value={otherText}
          onChange={(e) => setOtherText(e.target.value)}
        />
      )}
    </div>
  );

  return (
    <div className="container" style={{ padding: "2rem 1.5rem 4rem", maxWidth: 820 }}>
      <Link to="/admin/claims" className="back-link">
        <ArrowLeft size={16} />
        <span>Back to Claim Management</span>
      </Link>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "1rem 0" }}>
        <h1 className="page-title" style={{ margin: 0 }}>Review Claim</h1>
        <StatusBadge status={claim.status} />
      </div>

      {error && <div className="form-error-msg" style={{ marginBottom: "1rem" }}><span>{error}</span></div>}

      {/* Item info */}
      <div style={box}>
        <div style={label}>Item</div>
        <h3 style={{ fontSize: "1.15rem", fontWeight: 800, margin: "0.2rem 0 0.6rem" }}>{claim.item_name}</h3>
        <div style={row}><span style={label}>Type: </span>{claim.item_type} · {claim.item_category}</div>
        <div style={row}><span style={label}>Location: </span>{claim.item_location}</div>
        <div style={row}><span style={label}>Description: </span>{claim.item_description}</div>
        <div style={row}><span style={label}>Item status: </span><StatusBadge status={claim.item_status} /></div>
        <div style={row}>
          <span style={label}>Reported by: </span>
          {claim.reporter_name} · {claim.reporter_email} · +91 {claim.reporter_phone}
        </div>
        {claim.item_image_visibility !== "NONE" && claim.item_image && (
          <div style={{ marginTop: "0.75rem" }}>
            <div style={{ ...label, display: "flex", alignItems: "center", gap: "0.3rem" }}>
              {claim.item_image_visibility === "PRIVATE" && <Lock size={12} />}
              {claim.item_image_visibility === "PRIVATE" ? "Private image (admin only)" : "Item image"}
            </div>
            <img
              src={claim.item_image}
              alt={claim.item_name}
              style={{ marginTop: "0.4rem", maxWidth: 260, width: "100%", borderRadius: 10, border: "1px solid #e2e8f0" }}
            />
          </div>
        )}
      </div>

      {/* Claimant info */}
      <div style={box}>
        <div style={label}>Claimant</div>
        <div style={{ ...row, marginTop: "0.3rem" }}><strong>{claim.claimant_name}</strong></div>
        <div style={row}><span style={label}>Email: </span>{claim.claimant_email}</div>
        <div style={row}><span style={label}>Phone: </span>{claim.claimant_phone || "—"}</div>
        <div style={row}><span style={label}>Submitted: </span>{claim.date_claimed}</div>
      </div>

      {/* Verification */}
      <div style={{ ...box, background: "#fffbeb", borderColor: "#fde68a" }}>
        <div style={{ ...label, color: "#92400e", display: "flex", gap: "0.3rem", alignItems: "center" }}>
          <ShieldCheck size={13} /> Verification — compare these two
        </div>
        <div style={{ marginTop: "0.6rem" }}>
          <div style={label}>Original private verification (finder)</div>
          <p style={{ margin: "0.2rem 0 0.8rem" }}>"{claim.item_private_detail || "No private detail provided."}"</p>
          <div style={label}>Claimant's verification detail</div>
          <p style={{ margin: "0.2rem 0 0" }}>"{claim.claim_detail}"</p>
        </div>
      </div>

      {/* Decision */}
      {isPending && (
        <div style={box}>
          <LocationPicker />
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
            <button
              className="btn btn-success"
              disabled={busy || locationInvalid}
              onClick={() => run(() => adminDecideClaim(claim.id, "APPROVED", chosenLocation), "Claim approved. Item marked CLAIMED, ready for pickup.")}
            >
              <Check size={16} /> Approve Claim &amp; Assign Location
            </button>
            <button
              className="btn btn-outline-danger"
              disabled={busy}
              onClick={() => run(() => adminDecideClaim(claim.id, "REJECTED"), "Claim rejected. Item stays ACTIVE.")}
            >
              <X size={16} /> Reject Claim
            </button>
          </div>
        </div>
      )}

      {/* Handover */}
      {isApproved && (
        <div style={box}>
          <div style={label}>Handover</div>
          <p style={{ margin: "0.3rem 0 0.8rem" }}>
            <strong>{claim.handover_location || "No location yet"}</strong> · {handoverStatusLabel(claim.handover_status)}
            {claim.reviewed_by_name && <span style={{ color: "#64748b" }}> · approved by {claim.reviewed_by_name}</span>}
          </p>
          {completed ? (
            <div style={{ color: "#059669", fontWeight: 700, display: "flex", gap: "0.4rem", alignItems: "center" }}>
              <CheckCircle2 size={18} /> Item recovered — handover completed.
            </div>
          ) : (
            <>
              <LocationPicker />
              <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
                <button
                  className="btn btn-secondary"
                  disabled={busy || locationInvalid}
                  onClick={() => run(() => adminUpdateHandover(claim.id, { handover_location: chosenLocation }), "Handover location saved.")}
                >
                  Save Location
                </button>
                <button
                  className="btn btn-success"
                  disabled={busy || !claim.handover_location}
                  onClick={() => run(() => adminMarkRecovered(claim.item_id), "Item marked RECOVERED. Handover completed.")}
                >
                  <CheckCircle2 size={16} /> Mark Recovered
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {claim.status === "REJECTED" && (
        <div style={{ ...box, color: "#b91c1c" }}>This claim was rejected. The item remains ACTIVE.</div>
      )}

      {toast && (
        <div className="toast-notice">
          <CheckCircle2 size={18} style={{ color: "#10b981" }} />
          <span>{toast}</span>
        </div>
      )}
    </div>
  );
};

export default AdminClaimReview;
