import { useState } from 'react';
import api from '../api';

export default function RegisterChild() {
  const [formData, setFormData] = useState({
    name: '', age: '', location: '', date_missing: '', guardian_contact: ''
  });
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!photo) {
      setErr("Please upload a photo");
      return;
    }
    setLoading(true); setMsg(''); setErr('');
    
    const data = new FormData();
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    data.append('photo', photo);

    try {
      await api.post('/children/register', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMsg('Case registered successfully with face encoding.');
      setFormData({ name: '', age: '', location: '', date_missing: '', guardian_contact: '' });
      setPhoto(null);
    } catch (error) {
      setErr(error.response?.data?.detail || "Error registering case. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{maxWidth: '800px'}}>
      <h1 className="page-title">Register a Missing Child</h1>
      <div className="card">
        {msg && <div style={{background:'var(--success)', color:'white', padding:'10px', borderRadius:'8px', marginBottom:'1rem'}}>{msg}</div>}
        {err && <div style={{background:'var(--danger)', color:'white', padding:'10px', borderRadius:'8px', marginBottom:'1rem'}}>{err}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="input-group">
              <label>Child's Name</label>
              <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Age</label>
              <input type="number" min="0" max="18" value={formData.age} onChange={e => setFormData({...formData, age: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Last Seen Location</label>
              <input type="text" value={formData.location} onChange={e => setFormData({...formData, location: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Date Missing</label>
              <input type="date" value={formData.date_missing} onChange={e => setFormData({...formData, date_missing: e.target.value})} required />
            </div>
          </div>
          <div className="input-group" style={{marginTop:'1.5rem'}}>
            <label>Guardian Contact Info</label>
            <input type="text" value={formData.guardian_contact} onChange={e => setFormData({...formData, guardian_contact: e.target.value})} required />
          </div>
          <div className="input-group" style={{marginTop:'1.5rem'}}>
            <label>Upload Photo</label>
            <input type="file" accept="image/png, image/jpeg, image/jpg" onChange={e => setPhoto(e.target.files[0])} required style={{background:'transparent', border:'1px dashed var(--primary-light)', padding:'2rem', textAlign:'center', cursor:'pointer'}} />
          </div>
          <button type="submit" className="btn-primary" disabled={loading} style={{marginTop:'2rem'}}>
            {loading ? 'Processing...' : 'Register Case'}
          </button>
        </form>
      </div>
    </div>
  );
}
