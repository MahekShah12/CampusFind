import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import ItemForm from "../components/ItemForm";

const ReportItem = () => {
  return (
    <div className="container-narrow" style={{ padding: "2rem 1.5rem" }}>
      <Link to="/" className="back-link">
        <ArrowLeft size={16} />
        <span>Back to Items</span>
      </Link>

      <div style={{ marginBottom: "2rem" }}>
        <h1 className="page-title">Report an Item</h1>
        <p className="page-subtitle">
          Help your campus community find what was lost or return what was found.
        </p>
      </div>

      <ItemForm />
    </div>
  );
};

export default ReportItem;
