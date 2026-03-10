import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const searchAssets = async () => {
    const response = await fetch(`http://localhost:8000/b2b/matches?query=${query}`, {
      headers: { "x-api-key": "SAFE_API_KEY_SAMPLE" },
    });
    const data = await response.json();
    setResults(data.matches);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Safiri Public Portal</h1>
      <p>Search for your unclaimed assets:</p>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your name or ID"
        style={{ padding: "0.5rem", width: "300px" }}
      />
      <button onClick={searchAssets} style={{ marginLeft: "1rem", padding: "0.5rem" }}>
        Search
      </button>

      <ul style={{ marginTop: "2rem" }}>
        {results.map((r, idx) => (
          <li key={idx}>
            {r.owner_name} - {r.asset_type} (Confidence: {r.confidence}%)
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
