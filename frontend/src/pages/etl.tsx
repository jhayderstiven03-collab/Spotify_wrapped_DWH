import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

interface TableStatus {
  name: string;
  record_count: number;
}

interface LastRun {
  audit_id: number;
  started_at: string;
  duration_ms: number;
  status: "success" | "error";
  history_new: number;
  artists_new: number;
  tracks_new: number;
  error_message: string | null;
}

interface EtlStatus {
  tables: TableStatus[];
  last_runs: LastRun[];
}

interface Step {
  phase: string;
  detail: string;
  ok: boolean;
}

interface EtlRunResult {
  audit_id: number;
  duration_ms: number;
  status: "success" | "error";
  steps: Step[];
}

export default function Etl() {
  const [status, setStatus] = useState<EtlStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatus = () =>
    apiFetch<EtlStatus>("/v1/etl/status")
      .then(setStatus)
      .finally(() => setLoading(false));

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSync = async () => {
    setRunning(true);
    setSteps([]);
    try {
      const result = await apiFetch<EtlRunResult>("/v1/etl/run", { method: "POST" });
      setSteps(result.steps);
      await fetchStatus();
    } catch {
      setSteps([{ phase: "Error", detail: "Falló la ejecución del ETL", ok: false }]);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl font-bold">ETL Runner</h1>
          <p className="text-zinc-400 text-sm">Estado del DWH y ejecución del pipeline</p>
        </div>
        <button
          onClick={handleSync}
          disabled={running}
          className="flex items-center gap-2 bg-green-500 hover:bg-green-400 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold px-5 py-2.5 rounded-md transition-colors"
        >
          {running && (
            <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
          )}
          {running ? "Sincronizando..." : "Sync Now"}
        </button>
      </div>

      {/* Tabla DWH */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-zinc-800">
          <h2 className="text-white text-sm font-semibold">Estado del DWH</h2>
        </div>
        {loading ? (
          <p className="text-zinc-500 text-xs p-5">Cargando...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-zinc-500 text-xs uppercase tracking-widest border-b border-zinc-800">
                <th className="text-left px-5 py-3">Tabla</th>
                <th className="text-right px-5 py-3">Registros</th>
              </tr>
            </thead>
            <tbody>
              {status?.tables.map((t) => (
                <tr key={t.name} className="border-b border-zinc-800/50 last:border-0">
                  <td className="px-5 py-3 text-white font-mono text-xs">{t.name}</td>
                  <td className="px-5 py-3 text-right text-green-400 font-semibold">
                    {t.record_count.toLocaleString("es-CO")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Log de pasos */}
      {steps.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-zinc-800">
            <h2 className="text-white text-sm font-semibold">Log de ejecución</h2>
          </div>
          <ul className="p-5 flex flex-col gap-2">
            {steps.map((s, i) => (
              <li key={i} className="flex items-start gap-3 text-xs">
                <span>{s.ok ? "✅" : "❌"}</span>
                <span className="text-zinc-400">
                  <span className="text-zinc-300 font-medium">{s.phase}:</span> {s.detail}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Historial */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-zinc-800">
          <h2 className="text-white text-sm font-semibold">Historial de ejecuciones</h2>
        </div>
        {loading ? (
          <p className="text-zinc-500 text-xs p-5">Cargando...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-zinc-500 text-xs uppercase tracking-widest border-b border-zinc-800">
                <th className="text-left px-5 py-3">Fecha</th>
                <th className="text-right px-5 py-3">Duración</th>
                <th className="text-right px-5 py-3">Estado</th>
                <th className="text-right px-5 py-3">Nuevos</th>
              </tr>
            </thead>
            <tbody>
              {status?.last_runs.map((r) => (
                <tr key={r.audit_id} className="border-b border-zinc-800/50 last:border-0">
                  <td className="px-5 py-3 text-zinc-400 text-xs">
                    {new Date(r.started_at).toLocaleString("es-CO")}
                  </td>
                  <td className="px-5 py-3 text-right text-zinc-400 text-xs">
                    {(r.duration_ms / 1000).toFixed(1)}s
                  </td>
                  <td className="px-5 py-3 text-right">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      r.status === "success"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-right text-zinc-400 text-xs">
                    {r.history_new} tracks
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}