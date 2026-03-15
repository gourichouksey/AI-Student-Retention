import React from "react";

export default function Recommendations({ items }) {
  const showScholarships = items.some((item) => item.toLowerCase().includes("scholarship"));
  return (
    <div className="card">
      <h3>Recommended Actions</h3>
      <div className="scroll-area">
        <ul>
          {items.length === 0 && <li>No actions yet</li>}
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>

      {showScholarships && (
        <div className="mini-links">
          <span className="hint">Scholarship resources (India)</span>
          <ul>
            <li>
              <a href="https://scholarships.gov.in/" target="_blank" rel="noreferrer">
                National Scholarship Portal
              </a>
            </li>
            <li>
              <a href="https://scholarshipportal.mp.nic.in/" target="_blank" rel="noreferrer">
                MP State Scholarship Portal
              </a>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}

