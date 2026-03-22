import { useState } from 'react';
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
      <div className="auth-card" style={{ flexWrap: 'wrap' }}>
        <h1 className="app-title">Missing Link: AI-Powered Child Identification</h1>
        
        {error && <div style={{width:'100%', color:'white', background:'var(--danger)', padding:'10px', borderRadius:'8px', textAlign:'center'}}>{error}</div>}
        {msg && <div style={{width:'100%', color:'white', background:'var(--success)', padding:'10px', borderRadius:'8px', textAlign:'center'}}>{msg}</div>}
        
        <div style={{ flex: '1 1 300px' }}>
          <h2 style={{color:'var(--primary-light)', marginBottom:'1.5rem'}}>Login</h2>
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

        <div style={{ flex: '1 1 300px', borderLeft: '1px solid var(--border-light)', paddingLeft: '3rem' }}>
          <h2 style={{color:'var(--primary-light)', marginBottom:'1.5rem'}}>Register</h2>
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
            <button type="submit" className="btn-primary" style={{marginTop:'1rem', background:'var(--bg-color)', color:'var(--primary-light)', border:'1px solid var(--primary-light)'}}>Create Account</button>
          </form>
        </div>
      </div>
    </div>
  );
}
