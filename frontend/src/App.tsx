import Map from "./components/Map";
import RightPanel from "./components/RightPanel";

export default function App() {
  return (
    <div className="h-screen w-screen flex">
      {/* MAP */}
      <div className="flex-1 h-full bg-gray-900">
        <Map />
      </div>
      {/* RIGHT PANEL */}
      <div className="w-1/3 bg-gray-800 border-l border-gray-700">
        <div className="text-white p-4">
          <RightPanel />
        </div>
      </div>
    </div>
  );
}
