import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import {
  Upload,
  Lock,
  CheckCircle,
  AlertCircle,
  Image as ImageIcon,
  RotateCcw,
  Sparkles,
  Search,
  Eye,
  EyeOff,
  Phone,
  X
} from "lucide-react";
import { CATEGORIES, LOCATIONS } from "../data/mockData";
import { useApp } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";

const ItemForm = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { addItem } = useApp();
  const { user } = useAuth();

  const initialType = searchParams.get("type") === "LOST" ? "LOST" : "FOUND";

  const [type, setType] = useState(initialType);
  const [itemName, setItemName] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [phone, setPhone] = useState("");
  const [imageVisibility, setImageVisibility] = useState("PUBLIC");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [fileName, setFileName] = useState("");
  const [privateDetail, setPrivateDetail] = useState("");
  const [reporterName, setReporterName] = useState(user?.name || "");
  const [reporterEmail, setReporterEmail] = useState(user?.email || "");

  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [createdItemId, setCreatedItemId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    const paramType = searchParams.get("type");
    if (paramType && (paramType === "LOST" || paramType === "FOUND")) {
      setType(paramType);
    }
  }, [searchParams]);

  // Handle local file image upload
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setFileName(file.name);
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
      if (errors.image) {
        setErrors((prev) => ({ ...prev, image: null }));
      }
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview("");
    setFileName("");
  };

  // Preset sample image for quick testing during hackathon demo!
  const setDemoImage = (url, name) => {
    setImagePreview(url);
    setFileName(name);
    if (errors.image) {
      setErrors((prev) => ({ ...prev, image: null }));
    }
  };

  // Validation
  const validateForm = () => {
    const newErrors = {};

    if (!itemName.trim()) {
      newErrors.itemName = "Item name is required.";
    }

    if (!category || category === "All") {
      newErrors.category = "Please select a valid category.";
    }

    if (!description.trim()) {
      newErrors.description = "Item description is required.";
    } else if (description.trim().length < 10) {
      newErrors.description = "Description should be at least 10 characters.";
    }

    if (!location || location === "All") {
      newErrors.location = "Please select a campus location.";
    }

    if (!date) {
      newErrors.date = "Date is required.";
    }

    // Phone Number validation (Required, 10 digits, starts with 6,7,8,9)
    const cleanedPhone = phone.trim().replace(/\D/g, "");
    if (!phone.trim()) {
      newErrors.phone = "Please enter a valid 10-digit mobile number.";
    } else if (!/^[6-9]\d{9}$/.test(cleanedPhone)) {
      newErrors.phone = "Please enter a valid 10-digit mobile number.";
    }

    // Image upload validation based on visibility
    if (imageVisibility !== "NONE" && !imagePreview) {
      newErrors.image = "Please upload an image of the item.";
    }

    if (type === "FOUND") {
      if (!privateDetail.trim()) {
        newErrors.privateDetail =
          "Private verification detail is required for found items to protect against false claims.";
      } else if (privateDetail.trim().length < 8) {
        newErrors.privateDetail =
          "Please enter a descriptive secret detail (at least 8 characters).";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError("");

    if (!validateForm()) {
      window.scrollTo({ top: 120, behavior: "smooth" });
      return;
    }

    // Fallback image used only when visibility isn't NONE, a real file
    // wasn't picked, and no demo preview URL was set either.
    const fallbackImageUrl =
      "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?auto=format&fit=crop&w=800&q=80";

    setIsSaving(true);
    try {
      // If a real file was picked, addItem() uploads it to the backend and
      // uses the returned URL. Otherwise we pass along the demo preview URL
      // (already public) or the fallback -- addItem() forces "" when
      // image_visibility is NONE regardless of what's passed here.
      const newItem = await addItem(
        {
          type,
          item_name: itemName.trim(),
          category,
          description: description.trim(),
          location,
          date_reported: date,
          phone: phone.trim().replace(/\D/g, ""),
          image_visibility: imageVisibility,
          image_url: imageFile ? "" : imagePreview || fallbackImageUrl,
          private_detail: type === "FOUND" ? privateDetail.trim() : "",
          reported_by: reporterName.trim() || "Campus Student",
          contact_email: reporterEmail.trim() || "student@campus.edu",
        },
        imageFile
      );

      setCreatedItemId(newItem.id);
      setIsSubmitted(true);
      window.scrollTo({ top: 80, behavior: "smooth" });
    } catch (err) {
      console.error("Failed to submit item", err);
      setSubmitError(
        err?.response?.data?.detail ||
          "Something went wrong submitting your report. Please make sure the backend server is running and try again."
      );
      window.scrollTo({ top: 120, behavior: "smooth" });
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetForm = () => {
    setItemName("");
    setCategory("");
    setDescription("");
    setLocation("");
    setDate(new Date().toISOString().split("T")[0]);
    setPhone("");
    setImageVisibility("PUBLIC");
    setImageFile(null);
    setImagePreview("");
    setFileName("");
    setPrivateDetail("");
    setReporterName("");
    setReporterEmail("");
    setErrors({});
    setIsSubmitted(false);
  };

  if (isSubmitted) {
    return (
      <div className="success-screen-card">
        <div className="success-check-icon">
          <CheckCircle size={44} />
        </div>
        <h2 className="success-title">✓ Item Reported Successfully</h2>
        <p className="success-desc">
          Your <strong>{type}</strong> report for <strong>{itemName}</strong> has been published to CampusFind. Fellow students can now find or claim it.
        </p>

        <div className="success-actions">
          <button
            onClick={() => navigate("/")}
            className="btn btn-primary btn-lg"
          >
            View Items
          </button>
          {createdItemId && (
            <button
              onClick={() => navigate(`/items/${createdItemId}`)}
              className="btn btn-secondary btn-lg"
            >
              View Item Details
            </button>
          )}
          <button
            onClick={handleResetForm}
            className="btn btn-secondary btn-lg"
          >
            Report Another Item
          </button>
        </div>
      </div>
    );
  }

  const validCategories = CATEGORIES.filter((c) => c !== "All");
  const validLocations = LOCATIONS.filter((l) => l !== "All");

  return (
    <form className="form-card" onSubmit={handleSubmit} noValidate>
      {/* Item Type Selector */}
      <div className="form-group">
        <label className="form-label">
          What would you like to report? <span className="required">*</span>
        </label>
        <div className="type-selector-pills">
          <button
            type="button"
            className={`type-pill-btn ${type === "FOUND" ? "active found" : ""}`}
            onClick={() => setType("FOUND")}
          >
            <Sparkles size={24} style={{ color: type === "FOUND" ? "#059669" : "#64748b" }} />
            <span className="pill-title">I Found Something</span>
            <span className="pill-desc">Found an item on campus and want to return it</span>
          </button>

          <button
            type="button"
            className={`type-pill-btn ${type === "LOST" ? "active lost" : ""}`}
            onClick={() => setType("LOST")}
          >
            <Search size={24} style={{ color: type === "LOST" ? "#d97706" : "#64748b" }} />
            <span className="pill-title">I Lost Something</span>
            <span className="pill-desc">Looking for a personal item misplaced on campus</span>
          </button>
        </div>
      </div>

      {/* Item Name */}
      <div className="form-group">
        <label className="form-label" htmlFor="item-name">
          Item Name <span className="required">*</span>
        </label>
        <input
          id="item-name"
          type="text"
          className={`form-input ${errors.itemName ? "input-error" : ""}`}
          placeholder="e.g. iPhone 14, Black Fossil Wallet, Casio Calculator..."
          value={itemName}
          onChange={(e) => setItemName(e.target.value)}
        />
        {errors.itemName && (
          <div className="form-error-msg">
            <AlertCircle size={14} />
            <span>{errors.itemName}</span>
          </div>
        )}
      </div>

      {/* Category & Location Grid */}
      <div className="form-grid-2">
        <div className="form-group">
          <label className="form-label" htmlFor="category">
            Category <span className="required">*</span>
          </label>
          <select
            id="category"
            className={`form-select ${errors.category ? "input-error" : ""}`}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Select Category</option>
            {validCategories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          {errors.category && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.category}</span>
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="location">
            Campus Location <span className="required">*</span>
          </label>
          <select
            id="location"
            className={`form-select ${errors.location ? "input-error" : ""}`}
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            <option value="">Select Location</option>
            {validLocations.map((loc) => (
              <option key={loc} value={loc}>
                {loc}
              </option>
            ))}
          </select>
          {errors.location && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.location}</span>
            </div>
          )}
        </div>
      </div>

      {/* Date & Mandatory Phone Number Grid */}
      <div className="form-grid-2">
        <div className="form-group">
          <label className="form-label" htmlFor="date">
            Date {type === "FOUND" ? "Found" : "Lost"} <span className="required">*</span>
          </label>
          <input
            id="date"
            type="date"
            className={`form-input ${errors.date ? "input-error" : ""}`}
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          {errors.date && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.date}</span>
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="phone">
            Contact Phone Number <span className="required">*</span>
          </label>
          <div style={{ position: "relative" }}>
            <input
              id="phone"
              type="tel"
              maxLength={10}
              className={`form-input ${errors.phone ? "input-error" : ""}`}
              placeholder="Enter your 10-digit phone number"
              value={phone}
              onChange={(e) => {
                const digitsOnly = e.target.value.replace(/\D/g, "").slice(0, 10);
                setPhone(digitsOnly);
                if (errors.phone) setErrors((prev) => ({ ...prev, phone: null }));
              }}
            />
          </div>
          {errors.phone && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.phone}</span>
            </div>
          )}
        </div>
      </div>

      {/* Optional Contact Names */}
      <div className="form-grid-2">
        <div className="form-group">
          <label className="form-label" htmlFor="reporter-name">
            Your Name / Roll No. (Optional)
          </label>
          <input
            id="reporter-name"
            type="text"
            className="form-input"
            placeholder="e.g. Priya Sharma"
            value={reporterName}
            onChange={(e) => setReporterName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reporter-email">
            Campus Email (Optional)
          </label>
          <input
            id="reporter-email"
            type="email"
            className="form-input"
            placeholder="student@campus.edu"
            value={reporterEmail}
            onChange={(e) => setReporterEmail(e.target.value)}
          />
        </div>
      </div>

      {/* Description */}
      <div className="form-group">
        <label className="form-label" htmlFor="description">
          Public Description <span className="required">*</span>
        </label>
        <textarea
          id="description"
          rows={3}
          className={`form-textarea ${errors.description ? "input-error" : ""}`}
          placeholder="Describe visible characteristics (color, brand, visible marks, exact room or bench where seen)..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        {errors.description && (
          <div className="form-error-msg">
            <AlertCircle size={14} />
            <span>{errors.description}</span>
          </div>
        )}
      </div>

      {/* FEATURE 1: Image Visibility Option */}
      <div className="form-group">
        <label className="form-label">
          Image Visibility <span className="required">*</span>
        </label>
        <div className="image-visibility-options">
          <label className={`visibility-radio-card ${imageVisibility === "PUBLIC" ? "selected" : ""}`}>
            <input
              type="radio"
              name="imageVisibility"
              value="PUBLIC"
              checked={imageVisibility === "PUBLIC"}
              onChange={() => setImageVisibility("PUBLIC")}
            />
            <div className="radio-content">
              <span className="radio-title">Public</span>
              <span className="radio-desc">Anyone can see this image</span>
            </div>
          </label>

          <label className={`visibility-radio-card ${imageVisibility === "PRIVATE" ? "selected" : ""}`}>
            <input
              type="radio"
              name="imageVisibility"
              value="PRIVATE"
              checked={imageVisibility === "PRIVATE"}
              onChange={() => setImageVisibility("PRIVATE")}
            />
            <div className="radio-content">
              <span className="radio-title">Private</span>
              <span className="radio-desc">Hide this image from public listings</span>
            </div>
          </label>

          <label className={`visibility-radio-card ${imageVisibility === "NONE" ? "selected" : ""}`}>
            <input
              type="radio"
              name="imageVisibility"
              value="NONE"
              checked={imageVisibility === "NONE"}
              onChange={() => {
                setImageVisibility("NONE");
                removeImage();
              }}
            />
            <div className="radio-content">
              <span className="radio-title">Don't upload</span>
              <span className="radio-desc">No image will be attached</span>
            </div>
          </label>
        </div>

        {imageVisibility === "PRIVATE" && (
          <div className="visibility-help-banner">
            <Lock size={15} style={{ color: "#b45309", flexShrink: 0 }} />
            <span>This image will be hidden from public listings and can be used for verification.</span>
          </div>
        )}
      </div>

      {/* Image Upload section (only shown if imageVisibility !== 'NONE') */}
      {imageVisibility !== "NONE" ? (
        <div className="form-group">
          <label className="form-label">
            Item Image <span className="required">*</span>
            {imageVisibility === "PRIVATE" && (
              <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "#b45309", marginLeft: "0.5rem" }}>
                (Private Upload)
              </span>
            )}
          </label>

          {imagePreview ? (
            <div className="image-preview-container">
              <img src={imagePreview} alt="Preview" className="image-preview-img" />
              <div className="image-preview-overlay">
                <span>
                  {fileName || "item-photo.jpg"}{" "}
                  {imageVisibility === "PRIVATE" && "(Hidden from public view)"}
                </span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                  onClick={removeImage}
                >
                  Change Image
                </button>
              </div>
            </div>
          ) : (
            <div>
              <label
                htmlFor="image-upload"
                className={`image-upload-dropzone ${errors.image ? "has-error" : ""}`}
              >
                <div className="upload-icon-circle">
                  <Upload size={24} />
                </div>
                <p style={{ fontWeight: 600, fontSize: "0.95rem", color: "#1e293b", marginBottom: "0.25rem" }}>
                  Click to upload an image from your device
                </p>
                <p style={{ fontSize: "0.82rem", color: "#64748b" }}>
                  Supports JPG, PNG, WEBP (Max 5MB)
                </p>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={handleImageChange}
                />
              </label>

              {/* Quick Demo Pre-fill Sample Image Helpers */}
              <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                <span style={{ fontSize: "0.78rem", color: "#64748b" }}>Demo quick photo:</span>
                <button
                  type="button"
                  className="btn-reset-filters"
                  style={{ fontSize: "0.76rem" }}
                  onClick={() =>
                    setDemoImage(
                      "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=800&q=80",
                      "sample-phone.jpg"
                    )
                  }
                >
                  + Phone sample
                </button>
                <button
                  type="button"
                  className="btn-reset-filters"
                  style={{ fontSize: "0.76rem" }}
                  onClick={() =>
                    setDemoImage(
                      "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
                      "sample-wallet.jpg"
                    )
                  }
                >
                  + Wallet sample
                </button>
                <button
                  type="button"
                  className="btn-reset-filters"
                  style={{ fontSize: "0.76rem" }}
                  onClick={() =>
                    setDemoImage(
                      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80",
                      "sample-backpack.jpg"
                    )
                  }
                >
                  + Backpack sample
                </button>
              </div>
            </div>
          )}

          {errors.image && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.image}</span>
            </div>
          )}
        </div>
      ) : (
        <div
          style={{
            padding: "0.85rem 1rem",
            backgroundColor: "#f1f5f9",
            borderRadius: "8px",
            fontSize: "0.88rem",
            color: "#64748b",
            marginBottom: "1.5rem",
          }}
        >
          No image will be uploaded for this item report.
        </div>
      )}

      {/* Private Verification Detail (Special Product Feature) */}
      {type === "FOUND" && (
        <div className="private-detail-card">
          <div className="private-detail-header">
            <Lock size={18} />
            <span>Private Verification Detail (Required for Found Items)</span>
            <span className="private-detail-badge">CONFIDENTIAL</span>
          </div>

          <p className="private-detail-help">
            Enter a detail that only the real owner would know (e.g. A specific sticker on the back, a unique mark/scratch, something inside the wallet, lockscreen wallpaper).
            <br />
            <strong>This information will NOT be shown publicly</strong>. It will be used to verify ownership claims.
          </p>

          <textarea
            rows={3}
            className={`form-textarea ${errors.privateDetail ? "input-error" : ""}`}
            placeholder="e.g. Small Harry Potter Deathly Hallows silver sticker inside bottom corner of case..."
            value={privateDetail}
            onChange={(e) => setPrivateDetail(e.target.value)}
          />

          {errors.privateDetail && (
            <div className="form-error-msg">
              <AlertCircle size={14} />
              <span>{errors.privateDetail}</span>
            </div>
          )}
        </div>
      )}

      {submitError && (
        <div className="form-error-msg" style={{ marginTop: "1rem" }}>
          <AlertCircle size={14} />
          <span>{submitError}</span>
        </div>
      )}

      {/* Submit Button */}
      <div style={{ marginTop: "2rem", display: "flex", gap: "1rem", alignItems: "center" }}>
        <button
          type="submit"
          className="btn btn-primary btn-lg"
          style={{ minWidth: 200 }}
          disabled={isSaving}
        >
          {isSaving ? "Submitting..." : `Submit ${type === "FOUND" ? "Found" : "Lost"} Report`}
        </button>
        <button
          type="button"
          className="btn btn-secondary btn-lg"
          onClick={() => navigate("/")}
          disabled={isSaving}
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ItemForm;
