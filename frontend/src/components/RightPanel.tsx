import { useEffect, useState } from "react";

export default function RightPanel() {
  const [stac, setStac] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/stac")
      .then((res) => res.json())
      .then(setStac);

    fetch("http://localhost:8000/stats")
      .then((res) => res.json())
      .then(setStats);
  }, []);

  return (
    <div className="w-[300px] h-full bg-zinc-900 text-white p-3 overflow-auto">
      <h3 className="text-lg font-semibold mb-2">STAC</h3>
      <pre className="text-xs mb-6">
        {stac ? JSON.stringify(stac, null, 2) : "Loading..."}
      </pre>

      <h3 className="text-lg font-semibold mb-2">Stats</h3>

      {stats ? (
        <div className="text-sm space-y-1">
          <div>Features: {stats.feature_count}</div>
          <div>Total population: {stats.total_population}</div>
          <div>Avg intensity: {stats.avg_intensity}</div>
        </div>
      ) : (
        "Loading..."
      )}
    </div>
  );
}
