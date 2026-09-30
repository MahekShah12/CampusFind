import React from "react";
import { Link } from "react-router-dom";
import { MapPin, Calendar, ArrowRight, Lock, Image as ImageIcon } from "lucide-react";
import StatusBadge from "./StatusBadge";

const ItemCard = ({ item }) => {
  const fallbackImage =
    "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?auto=format&fit=crop&w=800&q=80";

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    try {
      const options = { day: "numeric", month: "short", year: "numeric" };
      return new Date(dateStr).toLocaleDateString("en-US", options);
    } catch {
      return dateStr;
    }
  };

  const isPrivate = item.image_visibility === "PRIVATE";
  const isNone = item.image_visibility === "NONE" || (!item.image_url && !isPrivate);

  return (
    <div className="item-card">
      <div className="item-card-image-wrap">
        {isPrivate ? (
          <div className="card-private-image-box">
            <div className="card-private-content">
              <Lock size={22} className="card-lock-icon" />
              <span className="card-lock-text">🔒 Image hidden for privacy</span>
            </div>
          </div>
        ) : isNone ? (
          <div className="card-none-image-box">
            <div className="card-none-content">
              <ImageIcon size={26} className="card-none-icon" />
              <span className="card-none-text">No image provided</span>
            </div>
          </div>
        ) : (
          <img
            src={item.image_url || fallbackImage}
            alt={item.item_name}
            className="item-card-img"
            loading="lazy"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = fallbackImage;
            }}
          />
        )}

        <div className="item-card-badges">
          <StatusBadge type={item.type} />
          {item.status && item.status !== "ACTIVE" && (
            <StatusBadge status={item.status} />
          )}
        </div>
      </div>

      <div className="item-card-body">
        <div className="item-card-category">{item.category}</div>
        <h3 className="item-card-title" title={item.item_name}>
          {item.item_name}
        </h3>

        <div className="item-card-meta">
          <div className="meta-item">
            <MapPin size={15} className="meta-icon" />
            <span>{item.location}</span>
          </div>
          <div className="meta-item">
            <Calendar size={15} className="meta-icon" />
            <span>{formatDate(item.date_reported)}</span>
          </div>
        </div>

        <div className="item-card-footer">
          <Link to={`/items/${item.id}`} className="item-card-btn">
            <span>View Details</span>
            <ArrowRight size={15} />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ItemCard;
