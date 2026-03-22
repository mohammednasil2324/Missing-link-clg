import { useState, useEffect } from 'react';
import api from '../api';

export default function Alerts() {
  const [tab, setTab] = useState('new');
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchAlerts(tab === 'new' ? 0 : 1);
  }, [tab]);

  const fetchAlerts = async (isRead) => {
    try {
      const res = await api.get(`/alerts?is_read=${isRead}`);
      setAlerts(res.data.alerts);
    } catch (err) {
      console.error(err);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.put(`/alerts/${id}/read`);
      fetchAlerts(0);
    } catch (err) {
      alert("Error archiving alert.");
    }
  };

  return (
    <div>
      <h1 className="page-title">Alerts Board</h1>
      
      <div style={{display:'flex', gap:'1rem', marginBottom:'2rem', borderBottom:'1px solid var(--border-light)', paddingBottom:'1rem'}}>
        <button 
          onClick={() => setTab('new')}
          style={{background:'none', border:'none', fontSize:'1.2rem', fontWeight:600, color: tab === 'new' ? 'var(--primary-light)' : 'var(--text-muted)', cursor:'pointer', borderBottom: tab === 'new' ? '2px solid var(--primary-light)' : 'none', paddingBottom:'0.5rem'}}
        >
          🆕 New Alerts
        </button>
        <button 
          onClick={() => setTab('archive')}
          style={{background:'none', border:'none', fontSize:'1.2rem', fontWeight:600, color: tab === 'archive' ? 'var(--primary-light)' : 'var(--text-muted)', cursor:'pointer', borderBottom: tab === 'archive' ? '2px solid var(--primary-light)' : 'none', paddingBottom:'0.5rem'}}
        >
          ✅ Archive
        </button>
      </div>

      <div style={{display:'flex', flexDirection:'column', gap:'1.5rem'}}>
        {alerts.length === 0 ? (
          <div className="card" style={{color:'var(--text-muted)'}}>No alerts in this category.</div>
        ) : (
          alerts.map(a => {
            const isHighConf = a.confidence > 80;
            return (
              <div key={a.id} className="card" style={{borderLeft: `5px solid ${isHighConf ? 'var(--danger)' : 'var(--warning)'}`}}>
                <div style={{display:'flex', justifyContent:'space-between'}}>
                  <h3 style={{margin:0, color:'var(--primary-light)'}}>{a.message}</h3>
                  <span style={{color:'var(--text-muted)', fontSize:'0.85rem'}}>{a.created_at}</span>
                </div>
                <p style={{color:'var(--text-muted)', marginBottom:'1.5rem'}}>Confidence: {a.confidence.toFixed(1)}%</p>
                
                <div style={{display:'flex', gap:'1.5rem', marginBottom:'1.5rem'}}>
                  <div style={{flex:1, maxWidth:'200px'}}>
                     <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'5px'}}>Registered Photo</p>
                     <img src={`http://127.0.0.1:8000/${a.original_photo}`} style={{width:'100%', borderRadius:'12px'}} />
                  </div>
                  <div style={{flex:1, maxWidth:'200px'}}>
                     <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'5px'}}>Found Match</p>
                     <img src={`http://127.0.0.1:8000/${a.found_photo_path}`} style={{width:'100%', borderRadius:'12px'}} />
                  </div>
                </div>

                {tab === 'new' && (
                  <button className="btn-primary" onClick={() => markAsRead(a.id)} style={{width:'auto'}}>
                    Resolve / Mark as Read
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
