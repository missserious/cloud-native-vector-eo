import { Group, Panel, Separator } from "react-resizable-panels";
import Map from "./components/Map";
import LeftBottomPanel from "./components/LeftBottomPanel";
import LeftTopPanel from "./components/LeftTopPanel";
import { useEffect, useState } from "react";

export default function App() {
  // fetch STAC
  // TODO: export type StacItem
  const [stac, setStac] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/stac")
      .then((res) => res.json())
      .then(setStac);
  }, []);

  // Feature ID
  const [selectedUuid, setSelectedUuid] = useState<string | null>(null);

  return (
    <div className="h-screen w-screen overflow-hidden">
      {/* ROOT: horizontal split */}
      <Group orientation="horizontal" className="h-full w-full">
        {/* LEFT SIDEBAR */}
        <Panel minSize="20%" maxSize="80%" defaultSize="30%">
          <Group orientation="vertical" className="h-full w-full">
            {/* TOP */}
            <Panel minSize="20%" maxSize="80%" className="h-full bg-gray-700">
              <LeftTopPanel uuid={selectedUuid} />
            </Panel>

            <Separator className="h-0.5 bg-gray-300 cursor-row-resize" />

            {/* BOTTOM */}
            <Panel className="bg-gray-600">
              <LeftBottomPanel stac={stac} />
            </Panel>
          </Group>
        </Panel>

        {/* VERTICAL SEPARATOR */}
        <Separator className="w-0.5 bg-gray-300  cursor-col-resize" />

        {/* RIGHT MAP */}
        <Panel>
          <div className="h-full w-full relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <Map stac={stac} onSelectFeature={setSelectedUuid} />
            </div>
          </div>
        </Panel>
      </Group>
    </div>
  );
}
