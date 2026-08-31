import React from "react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/goal", label: "Goal", icon: "🎯" },
  { to: "/learning-path", label: "Learning Path", icon: "🗺️" },
  { to: "/recommendations", label: "Recommendations", icon: "✨" },
  { to: "/skills", label: "Skills", icon: "🧩" },
  { to: "/assessments", label: "Assessments", icon: "📝" },
  { to: "/progress", label: "Progress", icon: "📈" },
  { to: "/profile", label: "Profile", icon: "⚙️" },
];

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-slate-200 bg-white h-[calc(100vh-4rem)] sticky top-16 hidden md:block overflow-y-auto">
      <nav className="p-3 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`
            }
          >
            <span aria-hidden="true">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
