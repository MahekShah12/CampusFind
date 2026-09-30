import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Heart } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const Footer = () => {
  const { user, isAdmin } = useAuth();
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <div className="footer-brand" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <ShieldCheck size={18} style={{ color: "#2563eb" }} />
            <span>CampusFind</span>
            <span style={{ fontWeight: 400, color: "#64748b" }}>— College Lost &amp; Found</span>
          </div>
          <div className="footer-note" style={{ marginTop: "0.25rem" }}>
            Find what you lost. Return what you found.
          </div>
        </div>

        <div style={{ display: "flex", gap: "1.25rem", fontSize: "0.85rem", color: "#64748b" }}>
          <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
            Browse Items
          </Link>
          {!isAdmin && (
            <Link to="/report" style={{ textDecoration: "none", color: "inherit" }}>
              Report Item
            </Link>
          )}
          {user && (
            <Link
              to={isAdmin ? "/admin/claims" : "/my-claims"}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              {isAdmin ? "Claim Management" : "My Claims"}
            </Link>
          )}
        </div>

        <div className="footer-note">
          Built for College Campus Demo 🎓
        </div>
      </div>
    </footer>
  );
};

export default Footer;
