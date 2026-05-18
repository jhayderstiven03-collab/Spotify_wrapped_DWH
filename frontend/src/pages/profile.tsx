import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

interface UserProfile {
  spotify_id: string;
  display_name: string;
  email: string;
  country: string;
  followers: number;
  product: "free" | "premium";
}

export default function Profile() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<UserProfile>("/v1/profile/me")
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <p className="text-zinc-500 text-sm">No se pudo cargar el perfil.</p>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 flex items-center gap-6 mb-6">
        <div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center text-black text-2xl font-bold flex-shrink-0">
          {user.display_name.slice(0, 2).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-white text-xl font-bold">{user.display_name}</h1>
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
              user.product === "premium"
                ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : "bg-zinc-700 text-zinc-400"
            }`}>
              {user.product.toUpperCase()}
            </span>
          </div>
          <p className="text-zinc-400 text-sm">{user.email} · {user.country}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <p className="text-zinc-500 text-xs uppercase tracking-widest mb-1">Seguidores</p>
          <p className="text-white text-2xl font-bold">
            {user.followers.toLocaleString("es-CO")}
          </p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <p className="text-zinc-500 text-xs uppercase tracking-widest mb-1">País</p>
          <p className="text-white text-2xl font-bold">{user.country}</p>
        </div>
      </div>
    </div>
  );
}