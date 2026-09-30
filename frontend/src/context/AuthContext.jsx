import React, { createContext, useContext, useState } from "react";
import { loginDemo, USER_STORAGE_KEY } from "../services/api";

// Demo-only "login": pick a seeded user. No passwords / tokens.
const AuthContext = createContext();

const readSavedUser = () => {
  try {
    return JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || "null");
  } catch {
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(readSavedUser);

  const login = async (email) => {
    const res = await loginDemo(email);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(res.data));
    setUser(res.data);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem(USER_STORAGE_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAdmin: user?.role === "ADMIN",
        isStudent: user?.role === "STUDENT",
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
