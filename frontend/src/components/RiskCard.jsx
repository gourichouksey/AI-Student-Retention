import React from "react";

export default function RiskCard({ score }) {
  const pct = score != null ? Math.round(score * 100) : "--";
  return (
    <div className="card">
      <h3>Risk Score</h3>
      <div className="big">{pct}%</div>
      <p>Dropout probability</p>
    </div>
  );
}
