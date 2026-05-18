import { NavLink } from "react-router-dom";
import { logout } from "../lib/auth";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

interface UserProfile {
  display_name: string;
  email: string;
  product: "free" | "premium";
}

export default function Navbar() {
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    apiFetch<UserProfile>("/v1/profile/me")
      .then(setUser)
      .catch(() => null);
  }, []);

  const initials = user?.display_name
    ? user.display_name.slice(0, 2).toUpperCase()
    : "SP";

  return (
    <aside className="fixed top-0 left-0 h-screen w-40 bg-zinc-950 border-r border-zinc-800 flex flex-col px-4 py-6">
      {/* Brand */}
      <div className="mb-8">
        <p className="text-white font-bold text-sm">SoundPulse</p>
        <p className="text-zinc-500 text-xs">Spotify Analytics</p>
      </div>

      {/* Links */}
      <nav className="flex flex-col gap-1 flex-1">
        {[
          { to: "/dashboard", label: "Dashboard" },
          { to: "/profile", label: "Profile" },
          { to: "/etl", label: "ETL Runner" },
        ].map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `text-sm px-3 py-2 rounded-md transition-colors ${
                isActive
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-900"
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User + logout */}
      <div className="flex items-center gap-2 mt-4">
        <div className="w-7 h-7 rounded-full bg-green-500 flex items-center justify-center text-black text-xs font-bold flex-shrink-0">
          {initials}
        </div>
        <span className="text-zinc-400 text-xs truncate">{user?.display_name ?? "..."}</span>
      </div>
      <button
        onClick={logout}
        className="mt-3 text-xs text-zinc-600 hover:text-red-400 text-left transition-colors"
      >
        Log Out
      </button>
    </aside>
  );
}