import React, { useState, useEffect } from "react";

function App() {
  const [claims, setClaims] = useState([]);

  const fetchClaims = async () => {
    const res = await fetch("http://localhost:8000/claims/all");
    const data = await res.json();
    setClaims(data.claims);
  };

  const approveClaim = async (claim_id) => {
    // placeholder logic for approving claim
    alert("Claim approved: " + claim_id);
  };

  useEffect(() => { fetchClaims(); }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Safiri Admin Dashboard</h1>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Owner</th><th>Asset</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {claims.map((c, idx) => (
            <tr key={idx}>
              <td>{c.owner_name}</td>
              <td>{c.asset_type}</td>
              <td>{c.status}</td>
              <td>
                <button onClick={() => approveClaim(c.claim_id)}>Approve</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
