import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./components/UiState";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/AppLayout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Goal from "./pages/Goal";
import LearningPath from "./pages/LearningPath";
import Recommendations from "./pages/Recommendations";
import Skills from "./pages/Skills";
import Assessments from "./pages/Assessments";
import Chat from "./pages/Chat";
import Progress from "./pages/Progress";

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/goal" element={<Goal />} />
              <Route path="/learning-path" element={<LearningPath />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/skills" element={<Skills />} />
              <Route path="/assessments" element={<Assessments />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/progress" element={<Progress />} />
            </Route>

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
