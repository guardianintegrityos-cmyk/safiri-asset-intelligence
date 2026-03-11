import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("");
  const [results, setResults] = useState(null);
  const [fraudResults, setFraudResults] = useState({});
  const [networkStats, setNetworkStats] = useState(null);

  const countries = [
    { code: "", name: "All African Countries" },
    { code: "kenya", name: "Kenya" },
    { code: "nigeria", name: "Nigeria" },
    { code: "uganda", name: "Uganda" },
    { code: "tanzania", name: "Tanzania" },
    { code: "ghana", name: "Ghana" },
    { code: "south_africa", name: "South Africa" }
  ];

  const handleSearch = async () => {
    let url = `http://localhost:8000/search?query=${encodeURIComponent(query)}`;
    if (country) {
      url += `&country=${country}`;
    }
    const response = await fetch(url);
    const data = await response.json();
    setResults(data);
  };

  const checkFraud = async (identityId) => {
    const response = await fetch(`http://localhost:8000/fraud-check/${identityId}`);
    const data = await response.json();
    setFraudResults(prev => ({ ...prev, [identityId]: data.fraud_risk }));
  };

  const loadNetworkStats = async () => {
    const response = await fetch(`http://localhost:8000/network-stats`);
    const data = await response.json();
    setNetworkStats(data);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-blue-600 mb-8">Safiri Continental Asset Intelligence Network</h1>
      <div className="max-w-md mx-auto mb-4">
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-2"
        >
          {countries.map(c => (
            <option key={c.code} value={c.code}>{c.name}</option>
          ))}
        </select>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter any clue: name, ID, phone, account, or asset value"
          className="w-full p-2 border border-gray-300 rounded mb-4"
        />
        <div className="flex gap-2">
          <button
            onClick={handleSearch}
            className="flex-1 bg-blue-600 text-white p-2 rounded"
          >
            Search Continental Network
          </button>
          <button
            onClick={loadNetworkStats}
            className="bg-green-600 text-white p-2 rounded px-4"
          >
            Network Stats
          </button>
        </div>
      </div>
      {networkStats && (
        <div className="max-w-4xl mx-auto mb-8 bg-white p-4 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Continental Network Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(networkStats).map(([country, stats]) => (
              <div key={country} className="border p-3 rounded">
                <h3 className="font-semibold capitalize">{country.replace('_', ' ')}</h3>
                {stats.error ? (
                  <p className="text-red-500">Offline</p>
                ) : (
                  <div>
                    <p>Identities: {stats.total_identities?.toLocaleString() || 'N/A'}</p>
                    <p>Assets: {stats.total_assets?.toLocaleString() || 'N/A'}</p>
                    <p className="text-green-600">Operational</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {results && (
        <div className="mt-8 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold mb-4">Query: {results.query}</h2>
          {results.results.map((candidate, index) => (
            <div key={index} className="bg-white p-4 rounded shadow mb-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">
                  {candidate.identity.full_name}
                  {candidate.country && (
                    <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {candidate.country.toUpperCase()}
                    </span>
                  )}
                </h3>
                <div>
                  <span className="text-green-600 font-bold mr-4">
                    {(candidate.ownership_probability * 100).toFixed(1)}% Ownership Probability
                  </span>
                  <button
                    onClick={() => checkFraud(candidate.identity.identity_id)}
                    className="bg-red-500 text-white px-3 py-1 rounded text-sm"
                  >
                    Check Fraud
                  </button>
                </div>
              </div>
              <p>ID: {candidate.identity.national_id}</p>
              <p>Address: {candidate.identity.postal_address}</p>
              <p>Phone: {candidate.identity.phone}</p>
              <p>Email: {candidate.identity.email}</p>
              <h4 className="font-semibold mt-2">Assets:</h4>
              <ul className="list-disc list-inside">
                {candidate.assets.map(asset => (
                  <li key={asset.asset_id}>
                    {asset.asset_type}: {asset.amount} at {asset.institution} (Account: {asset.account_number})
                  </li>
                ))}
              </ul>
              {candidate.aliases.length > 0 && (
                <div>
                  <h4 className="font-semibold mt-2">Aliases:</h4>
                  <p>{candidate.aliases.map(alias => alias.name_variations).join(', ')}</p>
                </div>
              )}
              {fraudResults[candidate.identity.identity_id] !== undefined && (
                <div className="mt-2">
                  <span className={fraudResults[candidate.identity.identity_id] ? "text-red-600" : "text-green-600"}>
                    Fraud Risk: {fraudResults[candidate.identity.identity_id] ? "High" : "Low"}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
