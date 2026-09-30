import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Search, PlusCircle, FileText, Menu, X, LogOut, LayoutDashboard, ClipboardList } from "lucide-react";
import { useApp } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { myClaims, adminClaims } = useApp();
  const { user, isAdmin, logout } = useAuth();

  const pendingCount = isAdmin
    ? adminClaims.filter((c) => c.status === "PENDING").length
    : myClaims.filter((c) => c.status === "PENDING").length;

  const close = () => setMobileMenuOpen(false);
  const linkCls = ({ isActive }) => `nav-link ${isActive ? "active" : ""}`;
  const badge = (n) =>
    n > 0 && (
      <span
        style={{
          background: "#ef4444",
          color: "#fff",
          fontSize: "0.7rem",
          padding: "0.1rem 0.45rem",
          borderRadius: "9999px",
          fontWeight: "bold",
          marginLeft: "0.2rem",
        }}
      >
        {n}
      </span>
    );

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand-wrapper" onClick={() => setMobileMenuOpen(false)}>
          <div className="brand-logo-icon">
            <Search size={22} strokeWidth={2.5} />
          </div>
          <div className="brand-info">
            <div className="brand-name">
              Campus<span>Find</span>
            </div>
            <div className="brand-tag">College Lost &amp; Found</div>
          </div>
        </Link>

        {/* Desktop Nav */}
        <nav className={`nav-links ${mobileMenuOpen ? "mobile-open" : ""}`}>
          {user && (
            <NavLink to="/" className={linkCls} onClick={close} end>
              Home
            </NavLink>
          )}

          {user && !isAdmin && (
            <>
              <NavLink to="/report" className={linkCls} onClick={close}>
                <PlusCircle size={16} />
                Report Item
              </NavLink>
              <NavLink to="/my-reports" className={linkCls} onClick={close}>
                <ClipboardList size={16} />
                My Reports
              </NavLink>
              <NavLink to="/my-claims" className={linkCls} onClick={close}>
                <FileText size={16} />
                My Claims
                {badge(pendingCount)}
              </NavLink>
            </>
          )}

          {user && isAdmin && (
            <>
              <NavLink to="/admin" className={linkCls} onClick={close} end>
                <LayoutDashboard size={16} />
                Admin Dashboard
              </NavLink>
              <NavLink to="/admin/claims" className={linkCls} onClick={close}>
                <FileText size={16} />
                Claim Management
                {badge(pendingCount)}
              </NavLink>
            </>
          )}

          {user ? (
            <>
              <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                {user.name} · {user.role}
              </span>
              <button
                onClick={() => {
                  close();
                  logout();
                }}
                title="Switch user"
                className="btn-reset-filters"
                style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem", fontSize: "0.8rem", color: "#64748b" }}
              >
                <LogOut size={13} />
                Switch User
              </button>
              {!isAdmin && (
                <NavLink to="/report" className="nav-btn-report" onClick={close}>
                  <PlusCircle size={16} />
                  Report Lost / Found
                </NavLink>
              )}
            </>
          ) : (
            <NavLink to="/login" className="nav-btn-report" onClick={close}>
              Login
            </NavLink>
          )}
        </nav>

        {/* Mobile Toggle */}
        <button
          className="mobile-nav-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </header>
  );
};

export default Navbar;
