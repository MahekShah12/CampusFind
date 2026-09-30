import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { MapPin, Calendar, ArrowRight } from "lucide-react";
import { useApp } from "../context/AppContext";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";

// Student view: only items reported by the logged-in student.
const MyReports = () => {
  const { myItems } = useApp();
  const navigate = useNavigate();

  return (
    <div className="container" style={{ padding: "2.5rem 1.5rem 4rem" }}>
      <div className="page-header" style={{ borderBottom: "none", paddingBottom: "0.5rem" }}>
        <h1 className="page-title">My Reports</h1>
        <p className="page-subtitle">Lost and found items you reported, with their current status.</p>
      </div>

      {myItems.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="You haven't reported anything yet."
          description="Report a lost or found item and it will show up here."
          actionText="Report an Item"
          onAction={() => navigate("/report")}
        />
      ) : (
        <div className="claims-list">
          {myItems.map((item) => (
            <div key={item.id} className="claim-card" style={{ alignItems: "center" }}>
              <div className="claim-card-content">
                <div className="claim-card-top">
                  <div>
                    <h3 className="claim-item-name">{item.item_name}</h3>
                    <div className="claim-user-info">
                      <span>
                        <MapPin size={14} /> {item.location}
                      </span>
                      <span>
                        <Calendar size={14} /> {item.date_reported}
                      </span>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                    <StatusBadge type={item.type} />
                    <StatusBadge status={item.status} />
                  </div>
                </div>
                <div style={{ fontSize: "0.9rem", color: "#475569", margin: "0.5rem 0" }}>
                  Status: <strong>{item.status}</strong>
                </div>
                <div className="claim-actions">
                  <Link
                    to={`/items/${item.id}`}
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

export default MyReports;
