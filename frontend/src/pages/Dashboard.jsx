import { useState, useEffect } from 'react';
import { Activity, CheckCircle, Search, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../api';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: { staggerChildren: 0.1 } 
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: { type: "spring", stiffness: 300, damping: 24 }
  }
};

export default function Dashboard({ user }) {
  const [stats, setStats] = useState({ active_cases: 0, potential_matches: 0, reunited: 0 });
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/stats');
        setStats(res.data.metrics);
        setRecent(res.data.recent_activity);
      } catch (err) {
        console.error(err);
      }
    };
    fetchStats();
  }, []);

  return (
    <motion.div initial="hidden" animate="visible" variants={containerVariants}>
      <motion.h1 variants={itemVariants} className="page-title">Mission Overview</motion.h1>
      
      <motion.div variants={containerVariants} className="stats-grid">
        <motion.div variants={itemVariants} className="card">
          <div className="stat-label" style={{display:'flex', alignItems:'center', gap:'8px'}}><Search size={18}/> ACTIVE CASES</div>
          <h2 className="stat-val val-active">{stats.active_cases}</h2>
        </motion.div>
        <motion.div variants={itemVariants} className="card">
          <div className="stat-label" style={{display:'flex', alignItems:'center', gap:'8px'}}><Activity size={18}/> POTENTIAL MATCHES</div>
          <h2 className="stat-val val-matches">{stats.potential_matches}</h2>
        </motion.div>
        <motion.div variants={itemVariants} className="card">
          <div className="stat-label" style={{display:'flex', alignItems:'center', gap:'8px'}}><CheckCircle size={18}/> SUCCESSFULLY REUNITED</div>
          <h2 className="stat-val val-reunited">{stats.reunited}</h2>
        </motion.div>
      </motion.div>

      <motion.h2 variants={itemVariants} style={{color:'var(--primary)', marginBottom:'1.5rem', marginTop:'3rem'}}>Recent Activity</motion.h2>
      
      {recent.length === 0 ? (
        <motion.div variants={itemVariants} className="card" style={{textAlign:'center', color:'var(--text-muted)'}}>No recent alerts found.</motion.div>
      ) : (
        <motion.div variants={containerVariants}>
          {recent.map(alert => {
            const isHighConf = alert.confidence > 80;
            return (
              <motion.div variants={itemVariants} key={alert.id} className="activity-item" style={{borderLeft: `5px solid ${isHighConf ? 'var(--danger)' : 'var(--warning)'}`}}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                  <div>
                    <div style={{fontSize:'0.85rem', color:'var(--text-muted)', marginBottom:'5px'}}>{alert.created_at}</div>
                    <h4 style={{margin:0, color:'var(--text-main)', display:'flex', alignItems:'center', gap:'8px'}}>
                      {isHighConf && <AlertTriangle size={18} color="var(--danger)"/>}
                      {alert.message}
                    </h4>
                  </div>
                  <div className={isHighConf ? "badge badge-high" : "badge badge-manual"}>
                    {alert.confidence.toFixed(1)}% Match
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </motion.div>
  );
}
