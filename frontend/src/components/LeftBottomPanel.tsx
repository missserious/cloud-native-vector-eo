export default function LeftBottomPanel({ stac }: { stac: any }) {
  return (
    <div className="h-full w-full text-white p-3">
      <h3 className="text-lg font-semibold mb-2">STAC</h3>

      <pre className="text-xs p-2 rounded">
        {stac ? (
          JSON.stringify(stac, null, 2)
        ) : (
          <span className="text-gray-400">Loading STAC...</span>
        )}
      </pre>
    </div>
  );
}
