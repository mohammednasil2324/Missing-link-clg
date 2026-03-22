import { useState, useEffect } from 'react';
import api from '../api';

export default function Cases() {
  const [cases, setCases] = useState([]);
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newStatus, setNewStatus] = useState('');

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async (q = '') => {
    try {
      const res = await api.get(`/cases${q ? `?search=${q}` : ''}`);
      setCases(res.data.cases);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchCases(search);
  };

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/cases/${id}/status`, { status });
      setEditingId(null);
      fetchCases(search);
    } catch (err) {
      alert("Error updating status.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Case Management</h1>
      
      <form onSubmit={handleSearch} style={{marginBottom:'2rem', display:'flex', gap:'1rem', maxWidth:'600px'}}>
        <div className="input-group" style={{flex:1, marginBottom:0}}>
          <input 
            type="text" 
            placeholder="Search cases by name or location..." 
            value={search} 
            onChange={e => setSearch(e.target.value)} 
          />
        </div>
        <button type="submit" className="btn-primary" style={{width:'auto'}}>Search</button>
      </form>

      <div className="case-list">
        {cases.length === 0 ? (
          <div className="card" style={{color:'var(--text-muted)'}}>No matching cases found.</div>
        ) : (
          cases.map(c => (
            <div key={c.id} className="card case-card">
              <img src={`http://127.0.0.1:8000/${c.photo_path}`} className="case-img" />
              
              <div className="case-info">
                <h3 style={{margin:0, color:'var(--primary-light)', marginBottom:'5px'}}>
                  {c.name} (Age: {c.age})
                </h3>
                <p style={{margin:0, fontSize:'14px', color:'var(--text-muted)'}}>
                  Last Seen: {c.location} on {c.date_missing}
                </p>
                <p style={{margin:0, fontSize:'14px', color:'var(--text-muted)'}}>
                  Contact: {c.guardian_contact}
                </p>
              </div>

              <div className="case-actions">
                <p style={{margin:0, marginBottom:'5px', color:'var(--text-main)'}}>
                  Status: <b>{c.status}</b>
                </p>
                
                {editingId === c.id ? (
                  <div style={{display:'flex', flexDirection:'column', gap:'10px'}}>
                    <div className="input-group" style={{margin:0}}>
                      <select value={newStatus} onChange={e => setNewStatus(e.target.value)}>
                        <option value="Pending">Pending</option>
                        <option value="Verified">Verified</option>
                        <option value="Found">Found</option>
                        <option value="Reunited">Reunited</option>
                      </select>
                    </div>
                    <div style={{display:'flex', gap:'10px'}}>
                      <button className="btn-primary" style={{padding:'0.5rem', flex:1}} onClick={() => updateStatus(c.id, newStatus)}>Save</button>
                      <button className="btn-primary" style={{padding:'0.5rem', flex:1, background:'var(--border-light)', color:'var(--text-main)'}} onClick={() => setEditingId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <button className="btn-primary" onClick={() => { setEditingId(c.id); setNewStatus(c.status === "No Matches" ? "Missing" : c.status); }}>
                    Update Status
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
