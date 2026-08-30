import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LoadingState } from "./UiState";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingState label="Loading..." />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
