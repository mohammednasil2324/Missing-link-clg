import { useState } from 'react';
import { motion } from 'framer-motion';
import api from '../api';

export default function Login({ onLogin }) {
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ username: '', password: '', role: 'General User' });
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setMsg('');
    try {
      const res = await api.post('/auth/login', loginForm);
      localStorage.setItem('token', res.data.token);
      onLogin(res.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(''); setMsg('');
    try {
      const res = await api.post('/auth/register', registerForm);
      localStorage.setItem('token', res.data.token);
      onLogin(res.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="auth-container">
      <motion.div 
        className="auth-card" 
        style={{ flexWrap: 'wrap' }}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <h1 className="app-title" style={{ width: '100%', textAlign: 'center' }}>Missing Link: AI-Powered Child Identification</h1>
        
        {error && <motion.div initial={{opacity:0}} animate={{opacity:1}} style={{width:'100%', color:'white', background:'rgba(244, 63, 94, 0.8)', border: '1px solid var(--danger)', padding:'12px', borderRadius:'12px', textAlign:'center', fontWeight: '600'}}>{error}</motion.div>}
        {msg && <motion.div initial={{opacity:0}} animate={{opacity:1}} style={{width:'100%', color:'white', background:'rgba(52, 211, 153, 0.8)', border: '1px solid var(--success)', padding:'12px', borderRadius:'12px', textAlign:'center', fontWeight: '600'}}>{msg}</motion.div>}
        
        <div style={{ flex: '1 1 300px' }}>
          <h2 style={{color:'var(--primary-light)', marginBottom:'1.5rem', display: 'flex', alignItems: 'center', gap: '10px'}}>
            <div style={{width: '8px', height: '24px', background: 'var(--primary-gradient)', borderRadius: '4px'}}></div>
            Login Space
          </h2>
          <form onSubmit={handleLogin}>
            <div className="input-group">
              <label>Username</label>
              <input type="text" value={loginForm.username} onChange={e => setLoginForm({...loginForm, username: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input type="password" value={loginForm.password} onChange={e => setLoginForm({...loginForm, password: e.target.value})} required />
            </div>
            <button type="submit" className="btn-primary" style={{marginTop:'1rem'}}>Login</button>
          </form>
        </div>

        <div style={{ flex: '1 1 300px', borderLeft: '1px solid rgba(148, 163, 184, 0.1)', paddingLeft: '3rem' }}>
          <h2 style={{color:'var(--primary-light)', marginBottom:'1.5rem', display: 'flex', alignItems: 'center', gap: '10px'}}>
            <div style={{width: '8px', height: '24px', background: 'var(--primary-gradient)', borderRadius: '4px'}}></div>
            New Agent Registration
          </h2>
          <form onSubmit={handleRegister}>
            <div className="input-group">
              <label>New Username</label>
              <input type="text" value={registerForm.username} onChange={e => setRegisterForm({...registerForm, username: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>New Password</label>
              <input type="password" value={registerForm.password} onChange={e => setRegisterForm({...registerForm, password: e.target.value})} required />
            </div>
            <div className="input-group">
              <label>Role</label>
              <select value={registerForm.role} onChange={e => setRegisterForm({...registerForm, role: e.target.value})}>
                <option value="General User">General User</option>
                <option value="NGO/Police">NGO/Police</option>
                <option value="Admin">Admin</option>
              </select>
            </div>
            {(registerForm.role === 'Admin' || registerForm.role === 'NGO/Police') && (
              <div className="input-group">
                <label>Invite Code Required</label>
                <input type="password" value={registerForm.inviteCode || ''} onChange={e => setRegisterForm({...registerForm, inviteCode: e.target.value})} placeholder={`Enter Invite Code for ${registerForm.role}`} required />
              </div>
            )}
            <button type="submit" className="btn-primary" style={{marginTop:'1.5rem', background:'rgba(15, 23, 42, 0.8)', color:'var(--primary-light)', border:'1px solid var(--primary-light)', boxShadow: '0 0 15px rgba(56, 189, 248, 0.1)'}}>Create Account</button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
