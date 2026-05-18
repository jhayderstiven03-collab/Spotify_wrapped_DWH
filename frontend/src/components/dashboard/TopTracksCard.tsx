import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

interface Track {
  track_id: number;
  name: string;
  album_name: string;
  duration_ms: number;
}

function formatDuration(ms: number): string {
  const mins = Math.floor(ms / 60000);
  const secs = Math.floor((ms % 60000) / 1000).toString().padStart(2, "0");
  return `${mins}:${secs}`;
}

export default function TopTracksCard() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Track[]>("/v1/tracks/top")
      .then((data) => setTracks(data.slice(0, 5)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
      <h2 className="text-white text-sm font-semibold mb-4">Top 5 Tracks</h2>
      {loading ? (
        <p className="text-zinc-500 text-xs">Cargando...</p>
      ) : tracks.length === 0 ? (
        <p className="text-zinc-500 text-xs">Sin datos. Sincroniza el ETL primero.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {tracks.map((t, i) => (
            <li key={t.track_id} className="flex items-center gap-3">
              <span className="text-zinc-600 text-xs w-4">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm truncate">{t.name}</p>
                <p className="text-zinc-500 text-xs truncate">{t.album_name}</p>
              </div>
              <span className="text-zinc-400 text-xs">{formatDuration(t.duration_ms)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}