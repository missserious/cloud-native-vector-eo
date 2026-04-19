import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

export default function Map() {
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

      const map = new maplibregl.Map({
        container: mapContainer.current,

        style: {
          version: 8,

          // BASEMAP
          sources: {
            osm: {
              type: "raster",
              tiles: [
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
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

            // debug layer
            {
              id: "debug",
              type: "fill",
              source: "pm",
              "source-layer": "data", // data Layer
              paint: {
                "fill-color": "#ff0000",
                "fill-opacity": 0.4,
              },
            },
          ],
        },

        //  Ljubljana
        center: [14.5058, 46.0569],
        zoom: 12,
      });

      // map.on("click", (e) => {
      //   console.log("CLICK:", e.lngLat);
      // });

      // map.on("load", () => {
      //   map.setFilter("debug", ["==", ["get", "class_2021"], "Forests"]);
      // });

      map.on("click", "debug", (e) => {
        console.log("FEATURES:", e.features);
      });

      map.addControl(new maplibregl.NavigationControl(), "top-right");
      map.addControl(new maplibregl.FullscreenControl(), "top-right");

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
