import React from "react";

export default function MonitoringTable({ actions }) {
  return (
    <div className="card">
      <h3>Monitoring & Interventions</h3>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Action</th>
              <th>Status</th>
              <th>Outcome</th>
            </tr>
          </thead>
          <tbody>
            {actions.length === 0 && (
              <tr>
                <td colSpan="4">No interventions logged</td>
              </tr>
            )}
            {actions.map((a, i) => (
              <tr key={i}>
                <td>{a.student_id}</td>
                <td className="cell-wrap">{a.action}</td>
                <td>{a.status}</td>
                <td className="cell-wrap">{a.outcome || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

