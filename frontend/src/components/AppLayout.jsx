import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import FloatingChat from "./FloatingChat";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
      <FloatingChat />
    </div>
  );
}