import React from "react";
import { CheckCircle2, Clock, XCircle, Search, HelpCircle, ShieldCheck } from "lucide-react";

const StatusBadge = ({ status, type, size = "md" }) => {
  // If `type` is passed (LOST / FOUND)
  if (type) {
    const isLost = type.toUpperCase() === "LOST";
    return (
      <span className={`status-badge ${isLost ? "badge-lost" : "badge-found"}`}>
        {isLost ? <Search size={12} /> : <ShieldCheck size={12} />}
        {type.toUpperCase()}
      </span>
    );
  }

  // If `status` is passed
  const normalized = (status || "ACTIVE").toUpperCase();

  switch (normalized) {
    case "LOST":
      return (
        <span className="status-badge badge-lost">
          <Search size={12} />
          LOST
        </span>
      );
    case "FOUND":
      return (
        <span className="status-badge badge-found">
          <ShieldCheck size={12} />
          FOUND
        </span>
      );
    case "ACTIVE":
      return (
        <span className="status-badge badge-active">
          <Clock size={12} />
          ACTIVE
        </span>
      );
    case "CLAIMED":
      return (
        <span className="status-badge badge-claimed">
          <HelpCircle size={12} />
          CLAIMED
        </span>
      );
    case "RECOVERED":
      return (
        <span className="status-badge badge-recovered">
          <CheckCircle2 size={12} />
          RECOVERED
        </span>
      );
    case "PENDING":
      return (
        <span className="status-badge badge-pending">
          <Clock size={12} />
          PENDING
        </span>
      );
    case "APPROVED":
      return (
        <span className="status-badge badge-approved">
          <CheckCircle2 size={12} />
          APPROVED
        </span>
      );
    case "REJECTED":
      return (
        <span className="status-badge badge-rejected">
          <XCircle size={12} />
          REJECTED
        </span>
      );
    default:
      return <span className="status-badge badge-active">{status}</span>;
  }
};

export default StatusBadge;
