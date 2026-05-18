import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

interface Artist {
  artist_id: number;
  name: string;
  popularity: number | null;
}

export default function TopArtistCard() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Artist[]>("/v1/artists/top")
      .then((data) => setArtists(data.slice(0, 5)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
      <h2 className="text-white text-sm font-semibold mb-4">Top 5 Artists</h2>
      {loading ? (
        <p className="text-zinc-500 text-xs">Cargando...</p>
      ) : artists.length === 0 ? (
        <p className="text-zinc-500 text-xs">Sin datos. Sincroniza el ETL primero.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {artists.map((a, i) => (
            <li key={a.artist_id} className="flex items-center gap-3">
              <span className="text-zinc-600 text-xs w-4">{i + 1}</span>
              <span className="text-white text-sm flex-1 truncate">{a.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}