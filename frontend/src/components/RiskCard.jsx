import React from "react";

export default function RiskCard({ score }) {
  const pct = score != null ? Math.round(score * 100) : "--";
  return (
    <div className="card risk-card">
      <div className="risk-header">
        <h3>Risk Score</h3>
        <span className="pill">Dropout probability</span>
      </div>
      <div className="risk-body">
        <div className="big">{pct}%</div>
        <div className="risk-meter">
          <div className="risk-fill" style={{ width: `${pct === "--" ? 0 : pct}%` }} />
        </div>
        <div className="risk-scale">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>
    </div>
  );
}

