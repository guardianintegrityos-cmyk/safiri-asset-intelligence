// ClaimsDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ClaimsDashboard({country}) {
  const [claims, setClaims] = useState([]);
  useEffect(() => {
    axios.get(`/claims?country=${country}`).then(res => setClaims(res.data));
  }, [country]);
  
  return (
    <div>
      <h1 className="text-xl font-bold">Claims Dashboard - {country}</h1>
      <table className="table-auto w-full">
        <thead><tr><th>ID</th><th>Status</th><th>Amount</th></tr></thead>
        <tbody>
          {claims.map(c => <tr key={c.id}><td>{c.id}</td><td>{c.status}</td><td>{c.amount}</td></tr>)}
        </tbody>
      </table>
    </div>
  );
}
