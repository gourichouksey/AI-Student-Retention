import React from "react";

export default function Recommendations({ items }) {
  return (
    <div className="card">
      <h3>Recommended Actions</h3>
      <ul>
        {items.length === 0 && <li>No actions yet</li>}
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
