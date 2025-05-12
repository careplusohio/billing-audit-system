// /src/components/VisitDetail.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

const VisitDetail = () => {
  const { id } = useParams();
  const [visit, setVisit] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access");
    axios
      .get(`http://127.0.0.1:8000/api/visits/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setVisit(res.data))
      .catch(() => setError("Failed to fetch visit details."));
  }, [id]);

  if (error) return <div className="p-4 text-red-600">{error}</div>;
  if (!visit) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Visit Details</h2>
      <p><strong>Patient:</strong> {visit.patient}</p>
      <p><strong>Provider:</strong> {visit.provider}</p>
      <p><strong>Date:</strong> {visit.visit_date}</p>
      <p><strong>Time:</strong> {visit.visit_time}</p>
      <p><strong>Notes:</strong> {visit.notes || "—"}</p>

      <Link to="/visits" className="mt-4 inline-block bg-gray-600 text-white px-4 py-2 rounded">← Back to List</Link>
    </div>
  );
};

export default VisitDetail;
