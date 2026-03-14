import React from "react";

export default function ShapPlot({ data }) {
  const items = data?.top_features || [];
  const maxAbs = items.length
    ? Math.max(...items.map((f) => Math.abs(f.impact)))
    : 1;
  const labelMap = {
    num__attendance_pct: "Attendance (%)",
    num__backlogs: "Backlogs (count)",
    num__family_income: "Family income (INR)",
    num__grade_math: "Math grade (0-100)",
    num__grade_science: "Science grade (0-100)",
    num__grade_english: "English grade (0-100)",
    cat__parents_edu: "Parents education",
    cat__scholarship_status: "Scholarship status",
  };
  const formatLabel = (name) => labelMap[name] || name.replace(/_/g, " ");
  return (
    <div className="card shap-card">
      <div className="card-header shap-header">
        <div>
          <span className="eyebrow">SHAP Impact</span>
          <h3>Risk Drivers</h3>
        </div>
        <span className="hint">Feature impact on dropout risk</span>
      </div>
      <div className="legend compact">
        <span className="dot pos" /> Increases risk
        <span className="dot neg" /> Decreases risk
        <span className="hint">Scale: 0 to {maxAbs.toFixed(2)}</span>
      </div>
      <div className="scroll-area">
        <div className="table-wrap">
          <table className="table shap-table">
            <thead>
              <tr>
                <th>Feature</th>
                <th>Impact</th>
                <th>Direction</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && (
                <tr>
                  <td colSpan="3">No SHAP data available</td>
                </tr>
              )}
              {items.map((f) => {
                const direction = f.impact >= 0 ? "Increases" : "Decreases";
                const directionClass = f.impact >= 0 ? "pos" : "neg";
                return (
                  <tr key={f.name}>
                    <td className="cell-wrap">{formatLabel(f.name)}</td>
                    <td className={`impact ${directionClass}`}>
                      {f.impact >= 0 ? "+" : ""}{f.impact.toFixed(2)}
                    </td>
                    <td className={directionClass}>{direction}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

