import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  getItems,
  getMyItems,
  getMyClaims,
  getAdminClaims,
  getAdminStats,
  createItem,
  createClaim,
  decideClaim,
  updateHandover,
  markItemRecovered,
  uploadImage
} from "../services/api";
import { useAuth } from "./AuthContext";

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const { user, isAdmin, isStudent } = useAuth();

  const [items, setItems] = useState([]);
  const [myItems, setMyItems] = useState([]); // student: items I reported
  const [myClaims, setMyClaims] = useState([]); // student: claims I submitted
  const [adminClaims, setAdminClaims] = useState([]); // admin only
  const [adminStats, setAdminStats] = useState(null); // admin only
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const refreshItems = useCallback(async () => {
    const res = await getItems();
    setItems(res.data);
  }, []);

  const refreshMine = useCallback(async () => {
    const [i, c] = await Promise.all([getMyItems(), getMyClaims()]);
    setMyItems(i.data);
    setMyClaims(c.data);
  }, []);

  const refreshAdmin = useCallback(async () => {
    const [c, s] = await Promise.all([getAdminClaims(), getAdminStats()]);
    setAdminClaims(c.data);
    setAdminStats(s.data);
  }, []);

  const loadAll = useCallback(async () => {
    setIsLoading(true);
    setLoadError("");
    try {
      await refreshItems();
      if (isStudent) await refreshMine();
      if (isAdmin) await refreshAdmin();
    } catch (err) {
      console.error("Failed to load CampusFind data", err);
      setLoadError(
        "Could not reach the CampusFind backend. Make sure the API server is running at http://127.0.0.1:8000."
      );
    } finally {
      setIsLoading(false);
    }
  }, [refreshItems, refreshMine, refreshAdmin, isStudent, isAdmin]);

  // Reload whenever the demo user changes (login / logout / switch role).
  useEffect(() => {
    setMyItems([]);
    setMyClaims([]);
    setAdminClaims([]);
    setAdminStats(null);
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.email]);

  // Create a new reported item (Lost or Found). Uploads the image first
  // if an actual File object was provided instead of a ready-made URL.
  const addItem = async (itemData, imageFile) => {
    let image_url = itemData.image_url || "";

    if (imageFile && itemData.image_visibility !== "NONE") {
      const uploadRes = await uploadImage(imageFile);
      image_url = uploadRes.data.image_url;
      if (image_url.startsWith("/")) {
        image_url = `http://127.0.0.1:8000${image_url}`;
      }
    }

    const res = await createItem({
      ...itemData,
      image_url: itemData.image_visibility === "NONE" ? "" : image_url
    });
    await Promise.all([refreshItems(), isStudent ? refreshMine() : Promise.resolve()]);
    return res.data;
  };

  const getItemById = (id) => {
    const numId = Number(id);
    return items.find((item) => item.id === numId);
  };

  // Student: submit a claim (identity comes from the logged-in user)
  const addClaim = async (claimData) => {
    const res = await createClaim(claimData);
    await refreshMine();
    return res.data;
  };

  // ---- Admin actions (backend re-checks the ADMIN role) ----
  const afterAdminChange = async () => {
    await Promise.all([refreshAdmin(), refreshItems()]);
  };

  const adminDecideClaim = async (claimId, status, handover_location) => {
    const res = await decideClaim(claimId, { status, handover_location });
    await afterAdminChange();
    return res.data;
  };

  const adminUpdateHandover = async (claimId, payload) => {
    const res = await updateHandover(claimId, payload);
    await afterAdminChange();
    return res.data;
  };

  const adminMarkRecovered = async (itemId) => {
    const res = await markItemRecovered(itemId);
    await afterAdminChange();
    return res.data;
  };

  return (
    <AppContext.Provider
      value={{
        items,
        myItems,
        myClaims,
        adminClaims,
        adminStats,
        isLoading,
        loadError,
        addItem,
        getItemById,
        addClaim,
        adminDecideClaim,
        adminUpdateHandover,
        adminMarkRecovered,
        refreshItems,
        reload: loadAll
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
