import React from "react";

export default function ShapPlot({ data }) {
  const items = data?.top_features || [];
  const maxAbs = items.length
    ? Math.max(...items.map((f) => Math.abs(f.impact)))
    : 1;
  return (
    <div className="card">
      <div className="card-header">
        <h3>SHAP Impact</h3>
        <span className="hint">Feature contribution to risk</span>
      </div>
      <div className="legend">
        <span className="dot pos" /> Increases risk
        <span className="dot neg" /> Decreases risk
      </div>
      <div className="axis">
        <span>0</span>
        <span>{(maxAbs / 2).toFixed(2)}</span>
        <span>{maxAbs.toFixed(2)}</span>
      </div>
      <div className="bars">
        {items.map((f) => {
          const magnitude = Math.min((Math.abs(f.impact) / maxAbs) * 100, 100);
          const direction = f.impact >= 0 ? "pos" : "neg";
          return (
            <div className="bar" key={f.name}>
              <span>{f.name}</span>
              <div className="barline">
                <div
                  className={`barfill ${direction}`}
                  style={{ width: `${magnitude}%` }}
                  title={`${f.name}: ${f.impact.toFixed(4)}`}
                />
              </div>
              <span className={direction === "pos" ? "pos" : "neg"}>{f.impact.toFixed(2)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
