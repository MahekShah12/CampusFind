import React from "react";
import { Filter, MapPin, Tag } from "lucide-react";
import { CATEGORIES, LOCATIONS } from "../data/mockData";

const FilterBar = ({
  selectedType,
  setSelectedType,
  selectedCategory,
  setSelectedCategory,
  selectedLocation,
  setSelectedLocation,
  onReset,
  hasActiveFilters,
}) => {
  return (
    <div className="filter-controls">
      {/* Type Toggle: All / Lost / Found */}
      <div className="type-toggle-group">
        <button
          className={`type-toggle-btn ${selectedType === "ALL" ? "active" : ""}`}
          onClick={() => setSelectedType("ALL")}
        >
          All Items
        </button>
        <button
          className={`type-toggle-btn ${selectedType === "LOST" ? "active lost" : ""}`}
          onClick={() => setSelectedType("LOST")}
        >
          Lost
        </button>
        <button
          className={`type-toggle-btn ${selectedType === "FOUND" ? "active found" : ""}`}
          onClick={() => setSelectedType("FOUND")}
        >
          Found
        </button>
      </div>

      {/* Dropdown Filters: Category & Location */}
      <div className="dropdown-filters">
        <div className="filter-select-wrapper">
          <Tag size={15} style={{ color: "#64748b" }} />
          <label htmlFor="category-select">Category:</label>
          <select
            id="category-select"
            className="filter-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat === "All" ? "All Categories" : cat}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-select-wrapper">
          <MapPin size={15} style={{ color: "#64748b" }} />
          <label htmlFor="location-select">Location:</label>
          <select
            id="location-select"
            className="filter-select"
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
          >
            {LOCATIONS.map((loc) => (
              <option key={loc} value={loc}>
                {loc === "All" ? "All Locations" : loc}
              </option>
            ))}
          </select>
        </div>

        {hasActiveFilters && (
          <button className="btn-reset-filters" onClick={onReset}>
            Reset Filters
          </button>
        )}
      </div>
    </div>
  );
};

export default FilterBar;
