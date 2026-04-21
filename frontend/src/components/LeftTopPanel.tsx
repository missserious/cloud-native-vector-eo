import { useEffect, useState } from "react";

export default function LeftBottomPanel({ uuid }: { uuid: string | null }) {
  const [stats, setStats] = useState<any>(null);
  const [feature, setFeature] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/stats")
      .then((res) => res.json())
      .then(setStats);
  }, []);

  // Fetch data for the selected feature whenever the uuid changes
  useEffect(() => {
    if (!uuid) return;

    fetch(`http://localhost:8000/features/${uuid}`)
      .then((res) => res.json())
      .then(setFeature);
  }, [uuid]);

  return (
    <>
      {/* Feature */}
      <div className="p-3 text-white">
        <h3 className="text-lg font-semibold mb-2">Selected Feature</h3>

        <div className="text-xs p-2 rounded space-y-1">
          {!uuid ? (
            <>
              <div className="text-gray-400">No feature selected</div>
              <div className="text-gray-400">
                ⚠️ Please select a feature on the map.
              </div>
            </>
          ) : !feature ? (
            <div className="text-gray-400">Loading feature...</div>
          ) : (
            Object.entries(feature).map(([key, value]) => (
              <div key={key}>
                <span className="font-semibold">{key}:</span>{" "}
                {typeof value === "object"
                  ? JSON.stringify(value)
                  : String(value)}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="h-full w-full text-white p-3">
        <h3 className="text-lg font-semibold mb-2">Statistics</h3>

        <div className="text-xs p-2 rounded">
          {stats ? (
            <>
              <div>Features: {stats.feature_count}</div>
              <div>Total population: {stats.total_population}</div>
              <div>Avg intensity: {stats.avg_intensity}</div>
            </>
          ) : (
            <>
              {" "}
              <div className="text-gray-400">Loading statistics...</div>
              <div className="text-gray-400">
                ⚠️ Statistics are only available for the dataset:
                ndvi-change-vector-result-example.
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
