import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: { staggerChildren: 0.15 } 
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0, scale: 0.95 },
  visible: { 
    y: 0, 
    opacity: 1,
    scale: 1,
    transition: { type: "spring", stiffness: 200, damping: 20 }
  }
};

export default function Search() {
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState(null);
  const [err, setErr] = useState('');

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSearch = async () => {
    if (!photo) return;
    setLoading(true); setErr(''); setMatches(null);
    const data = new FormData();
    data.append('photo', photo);

    try {
      const res = await api.post('/search', data);
      setMatches(res.data.matches);
      if (res.data.matches.length === 0) {
        setErr(res.data.message || "No matches found.");
      }
    } catch (error) {
      setErr(error.response?.data?.detail || "Facial extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  const generateAlert = async (match) => {
    try {
      await api.post('/alerts', {
        child_id: match.child.id,
        confidence: match.confidence,
        found_photo_path: match.found_photo_path,
        status: "Pending"
      });
      alert(`Alert generated for ${match.child.name}!`);
    } catch (error) {
      alert("Error generating alert.");
    }
  };

  return (
    <motion.div initial="hidden" animate="visible" variants={containerVariants}>
      <motion.h1 variants={itemVariants} className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <div style={{width: '6px', height: '32px', background: 'var(--primary-gradient)', borderRadius: '3px'}}></div>
        Identify a Found Child
      </motion.h1>
      
      <motion.div variants={itemVariants} className="card" style={{maxWidth:'600px'}}>
        <div className="input-group">
          <label>Upload Photo of found child</label>
          <input type="file" accept="image/png, image/jpeg, image/jpg" onChange={handlePhotoChange} style={{border:'1px dashed var(--primary-light)', padding:'1.5rem'}} />
        </div>
        
        <AnimatePresence>
          {preview && (
            <motion.div 
              initial={{opacity: 0, height: 0}} 
              animate={{opacity: 1, height: 'auto'}} 
              exit={{opacity: 0, height: 0}}
              style={{textAlign:'center', margin:'1.5rem 0', overflow:'hidden'}}
            >
              <img src={preview} alt="Preview" style={{borderRadius:'12px', border:'1px solid var(--border-light)', maxHeight:'250px'}} />
            </motion.div>
          )}
        </AnimatePresence>
        
        <button className="btn-primary" onClick={handleSearch} disabled={!photo || loading}>
          {loading ? 'Scanning Database...' : 'Search Database'}
        </button>
        
        {err && <motion.div initial={{opacity:0}} animate={{opacity:1}} style={{marginTop:'1.5rem', color:'var(--danger)', background:'rgba(244, 63, 94, 0.1)', border: '1px solid var(--danger)', padding:'12px', borderRadius:'12px', textAlign:'center', fontWeight: '600'}}>{err}</motion.div>}
      </motion.div>

      <AnimatePresence>
        {matches && matches.length > 0 && (
          <motion.div initial="hidden" animate="visible" variants={containerVariants} style={{marginTop:'3rem'}}>
            <motion.h2 variants={itemVariants} style={{color:'var(--text-main)', marginBottom:'1.5rem', display: 'flex', alignItems: 'center', gap: '10px'}}>
              <div style={{width: '6px', height: '24px', background: 'var(--primary-gradient)', borderRadius: '3px'}}></div>
              Found {matches.length} Potential Matches
            </motion.h2>
            
            <div style={{display:'flex', flexDirection:'column', gap:'2rem'}}>
              {matches.map((m, idx) => (
                <motion.div variants={itemVariants} key={idx} className="card">
                  <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'15px'}}>
                    <h3 style={{color:'var(--primary-light)', margin:0}}>{m.child.name}</h3>
                    <span className={m.confidence > 80 ? "badge badge-high" : "badge badge-manual"}>
                      {m.confidence.toFixed(1)}% Confidence
                    </span>
                  </div>
                  
                  <p style={{color:'var(--text-muted)', marginBottom:'15px'}}>
                    Last seen: {m.child.location} | Age: {m.child.age}
                  </p>
                  
                  <div style={{width:'100%', background:'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius:'10px', height:'10px', marginBottom:'20px'}}>
                    <motion.div 
                      initial={{width: 0}}
                      animate={{width: `${Math.min(m.confidence, 100)}%`}}
                      transition={{duration: 1, ease: 'easeOut', delay: 0.3 * idx}}
                      style={{height:'100%', borderRadius:'10px', background:'var(--primary-gradient)'}}
                    />
                  </div>
                  
                  <div style={{display:'flex', gap:'1.5rem', marginBottom:'1.5rem'}}>
                    <div style={{flex:1}}>
                      <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'5px'}}>Original</p>
                      <img src={`http://127.0.0.1:8000/${m.child.photo_path}`} style={{width:'100%', borderRadius:'12px'}} />
                    </div>
                    {m.aged_photo_path && (
                      <div style={{flex:1}}>
                        <p style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'5px'}}>Aged Simulation (+2y)</p>
                        <img src={`http://127.0.0.1:8000/${m.aged_photo_path}`} style={{width:'100%', borderRadius:'12px'}} />
                      </div>
                    )}
                  </div>
                  
                  <button className="btn-primary" onClick={() => generateAlert(m)}>
                    Generate Official Alert for {m.child.name}
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
