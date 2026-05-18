import TopArtistCard from "../components/dashboard/TopArtistCard";
import TopTracksCard from "../components/dashboard/TopTracksCard";
import PeakHourCard from "../components/dashboard/PeakHourCard";

export default function Dashboard() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-white text-2xl font-bold mb-1">Dashboard</h1>
      <p className="text-zinc-400 text-sm mb-6">Tu actividad musical personal</p>
      <div className="grid grid-cols-2 gap-4">
        <PeakHourCard />
        <TopArtistCard />
        <TopTracksCard />
      </div>
    </div>
  );
}