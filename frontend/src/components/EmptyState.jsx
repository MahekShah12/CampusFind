import React from "react";
import { SearchX, Inbox, AlertTriangle } from "lucide-react";

const EmptyState = ({
  icon = "search",
  title = "No items found",
  description = "Try another search or remove some filters.",
  actionText,
  onAction,
}) => {
  const renderIcon = () => {
    switch (icon) {
      case "inbox":
        return <Inbox size={32} />;
      case "error":
        return <AlertTriangle size={32} />;
      case "search":
      default:
        return <SearchX size={32} />;
    }
  };

  return (
    <div className="empty-state">
      <div className="empty-state-icon">{renderIcon()}</div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-desc">{description}</p>
      {actionText && onAction && (
        <button className="btn btn-secondary" onClick={onAction}>
          {actionText}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
