// /src/components/VisitAdd.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const VisitAdd = () => {
  const [form, setForm] = useState({
    patient: "",
    provider: "",
    visit_date: "",
    visit_time: "",
    notes: "",
  });

  const [patients, setPatients] = useState([]);
  const [providers, setProviders] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access");
    axios.get("http://127.0.0.1:8000/api/patients/", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setPatients(res.data));

    axios.get("http://127.0.0.1:8000/api/providers/", {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setProviders(res.data));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access");
    axios.post("http://127.0.0.1:8000/api/visits/add/", form, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(() => {
      alert("Visit added!");
      navigate("/visits");
    })
    .catch(() => alert("Failed to add visit."));
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Add Visit</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select name="patient" value={form.patient} onChange={handleChange} required className="border p-2 w-full rounded">
          <option value="">Select Patient</option>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
          ))}
        </select>

        <select name="provider" value={form.provider} onChange={handleChange} required className="border p-2 w-full rounded">
          <option value="">Select Provider</option>
          {providers.map((p) => (
            <option key={p.id} value={p.id}>{p.provider_name}</option>
          ))}
        </select>

        <input type="date" name="visit_date" value={form.visit_date} onChange={handleChange} className="border p-2 w-full rounded" required />
        <input type="time" name="visit_time" value={form.visit_time} onChange={handleChange} className="border p-2 w-full rounded" required />
        <textarea name="notes" value={form.notes} onChange={handleChange} className="border p-2 w-full rounded" placeholder="Notes (optional)" />

        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">➕ Add Visit</button>
      </form>
    </div>
  );
};

export default VisitAdd;
