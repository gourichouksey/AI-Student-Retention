import React from "react";

export default function HighRiskList({ students }) {
  return (
    <div className="card">
      <h3>High-Risk Students</h3>
      <div className="scroll-area">
        <ul>
          {students.length === 0 && <li>No records</li>}
          {students.map((s, i) => (
            <li key={i}>Student {s.student_id} — {Math.round(s.risk * 100)}%</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

