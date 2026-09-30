import React from "react";
import { useNavigate } from "react-router-dom";
import { Search, Sparkles, PlusCircle } from "lucide-react";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="hero-section">
      <div className="container">
        <div className="hero-pill">
          <span className="dot"></span>
          <span>Official Campus Lost &amp; Found Portal</span>
        </div>

        <h1 className="hero-title">
          Find what you lost.<br />
          <span>Return what you found.</span>
        </h1>

        <p className="hero-subtitle">
          A trusted Lost &amp; Found platform for your campus community. Reconnect lost belongings with their verified owners safely and quickly.
        </p>

        <div className="hero-actions">
          <button
            onClick={() => navigate("/report?type=LOST")}
            className="btn btn-lg btn-warning"
          >
            <Search size={18} />
            I LOST SOMETHING
          </button>

          <button
            onClick={() => navigate("/report?type=FOUND")}
            className="btn btn-lg btn-success"
          >
            <PlusCircle size={18} />
            I FOUND SOMETHING
          </button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
