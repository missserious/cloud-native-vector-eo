import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

export default function Map({
  stac,
  onSelectFeature,
}: {
  stac: any;
  onSelectFeature: (uuid: string) => void;
}) {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);

    const initMap = async () => {
      // fetch STAC from backend
      const res = await fetch("http://localhost:8000/stac", {
        cache: "no-store",
      });

      if (!res.ok) {
        console.error("Failed to load STAC");
        return;
      }

      const stac = await res.json();

      const tilesUrl = stac?.assets?.["vector-tiles"]?.href;

      if (!tilesUrl) {
        console.error("No tiles URL found in STAC");
        return;
      }

      console.log("SIGNED URL:", tilesUrl);

      // Map creation
      const map = new maplibregl.Map({
        // quick fix:
        container: mapContainer.current as HTMLElement,

        style: {
          version: 8,

          // BASEMAP
          sources: {
            osm: {
              type: "raster",
              tiles: [
                "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png",
              ],
              tileSize: 256,
              attribution: "© OpenStreetMap",
            },

            // TODO: url zum storage
            pm: {
              type: "vector",
              url: `pmtiles://${tilesUrl}`,
            },
          },

          layers: [
            // BASEMAP
            {
              id: "osm",
              type: "raster",
              source: "osm",
            },

            // slight overlay for contrast
            {
              id: "overlay",
              type: "background",
              paint: {
                "background-color": "rgba(0,0,0,0.1)",
              },
            },

            // tiles  layer
            {
              id: "tiles",
              type: "fill",
              source: "pm",
              "source-layer": "data", // data Layer defined in backend
              paint: {
                "fill-color": "#ff0000",
                "fill-opacity": 0.2,
              },
            },
          ],
        },

        //  Ljubljana (Fallback)
        // center: [14.5058, 46.0569],
        zoom: 12,
      });

      // map.on("click", (e) => {
      //   console.log("CLICK:", e.lngLat);
      // });

      // map.on("load", () => {
      //   map.setFilter("tiles", ["==", ["get", "class_2021"], "Forests"]);
      // });

      // BBOX FIT (HIER IST DER FIX)
      map.on("load", () => {
        if (stac?.bbox) {
          const [minLon, minLat, maxLon, maxLat] = stac.bbox;

          map.fitBounds(
            [
              [minLon, minLat],
              [maxLon, maxLat],
            ],
            {
              padding: 140,
              duration: 1000,
            },
          );
        }
      });

      map.on("click", "tiles", (e) => {
        const uuid = e.features?.[0]?.properties?.uuid;

        if (!uuid) return;

        onSelectFeature(uuid);
      });

      // Controls
      map.addControl(new maplibregl.NavigationControl(), "top-right");
      map.addControl(new maplibregl.FullscreenControl(), "top-right");
      map.addControl(new maplibregl.ScaleControl(), "bottom-left");

      mapRef.current = map;
    };

    initMap();

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={mapContainer} className="h-full w-full" />;
}
