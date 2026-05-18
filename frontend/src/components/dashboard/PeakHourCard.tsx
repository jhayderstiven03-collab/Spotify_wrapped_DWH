import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

interface PeakHour {
  hour: number;
  count: number;
}

export default function PeakHourCard() {
  const [data, setData] = useState<PeakHour | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<PeakHour>("/v1/history/peak-hour")
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  const formatHour = (h: number) =>
    `${String(h).padStart(2, "0")}:00 – ${String(h + 1).padStart(2, "0")}:00`;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
      <p className="text-zinc-500 text-xs uppercase tracking-widest mb-1">Peak Activity</p>
      <h2 className="text-white text-sm font-semibold mb-4">Peak Listening Hour</h2>
      {loading ? (
        <p className="text-zinc-500 text-xs">Cargando...</p>
      ) : !data ? (
        <p className="text-zinc-500 text-xs">Sin datos. Sincroniza el ETL primero.</p>
      ) : (
        <>
          <p className="text-green-500 text-4xl font-bold">{formatHour(data.hour)}</p>
          <p className="text-zinc-500 text-xs mt-2">{data.count} reproducciones en esta hora</p>
        </>
      )}
    </div>
  );
}