import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 sticky top-0 z-20">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-600 to-accent-500 flex items-center justify-center text-white font-bold text-sm">
          P
        </div>
        <span className="font-semibold text-lg tracking-tight hidden sm:block">Pathwise</span>
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <>
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium leading-tight">{user.name}</p>
              <p className="text-xs text-slate-500 leading-tight">{user.email}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-semibold">
              {user.name?.[0]?.toUpperCase() || "U"}
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
            >
              Log out
            </button>
          </>
        )}
      </div>
    </header>
  );
}
