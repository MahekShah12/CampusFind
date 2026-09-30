import React, { useState, useMemo } from "react";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import FilterBar from "../components/FilterBar";
import ItemCard from "../components/ItemCard";
import EmptyState from "../components/EmptyState";
import { useApp } from "../context/AppContext";

const Home = () => {
  const { items } = useApp();

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("ALL");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedLocation, setSelectedLocation] = useState("All");

  // Check if any filters are active
  const hasActiveFilters =
    searchTerm.trim() !== "" ||
    selectedType !== "ALL" ||
    selectedCategory !== "All" ||
    selectedLocation !== "All";

  const handleResetFilters = () => {
    setSearchTerm("");
    setSelectedType("ALL");
    setSelectedCategory("All");
    setSelectedLocation("All");
  };

  // Case-insensitive filtering
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      // Type filter (Lost / Found / All)
      if (selectedType !== "ALL" && item.type.toUpperCase() !== selectedType) {
        return false;
      }

      // Category filter
      if (selectedCategory !== "All" && item.category !== selectedCategory) {
        return false;
      }

      // Location filter
      if (selectedLocation !== "All" && item.location !== selectedLocation) {
        return false;
      }

      // Search term filter (check name, description, category, location)
      if (searchTerm.trim() !== "") {
        const query = searchTerm.toLowerCase().trim();
        const matchesName = item.item_name?.toLowerCase().includes(query);
        const matchesDesc = item.description?.toLowerCase().includes(query);
        const matchesCat = item.category?.toLowerCase().includes(query);
        const matchesLoc = item.location?.toLowerCase().includes(query);

        if (!matchesName && !matchesDesc && !matchesCat && !matchesLoc) {
          return false;
        }
      }

      return true;
    });
  }, [items, selectedType, selectedCategory, selectedLocation, searchTerm]);

  return (
    <div>
      {/* Hero Section */}
      <Hero />

      {/* Search & Filter Container */}
      <section className="search-filter-section">
        <div className="container">
          <div className="search-box-card">
            <h2 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "1rem" }}>
              Search Lost &amp; Found Items
            </h2>

            {/* Search Input */}
            <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

            {/* Filter Controls (Type, Category, Location) */}
            <FilterBar
              selectedType={selectedType}
              setSelectedType={setSelectedType}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              selectedLocation={selectedLocation}
              setSelectedLocation={setSelectedLocation}
              onReset={handleResetFilters}
              hasActiveFilters={hasActiveFilters}
            />
          </div>

          {/* Items Section Header */}
          <div className="section-header">
            <div className="section-title">
              <span>Recent Items</span>
              <span className="item-count-badge">
                {filteredItems.length} {filteredItems.length === 1 ? "item" : "items"}
              </span>
            </div>
            {hasActiveFilters && (
              <span style={{ fontSize: "0.88rem", color: "#64748b" }}>
                Filtered from {items.length} total items
              </span>
            )}
          </div>

          {/* Items Grid or Empty State */}
          {filteredItems.length > 0 ? (
            <div className="items-grid">
              {filteredItems.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <EmptyState
              icon="search"
              title="No items found."
              description="Try another search or remove some filters."
              actionText={hasActiveFilters ? "Clear All Filters" : undefined}
              onAction={handleResetFilters}
            />
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
