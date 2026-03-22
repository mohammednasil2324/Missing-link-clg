import { NavLink } from 'react-router-dom';
import { Home, UserPlus, Search as SearchIcon, Bell, Users, LogOut } from 'lucide-react';

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header" style={{textAlign: 'center', marginBottom: '1.5rem'}}>
        <div style={{
          width: '64px', height: '64px', borderRadius: '50%', background: 'var(--primary-gradient)', 
          margin: '0 auto 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: 'var(--shadow-glow)', color: 'white', fontWeight: 'bold', fontSize: '1.5rem'
        }}>
          {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
        </div>
        <p className="role-badge" style={{color: 'var(--primary-light)', fontSize: '0.8rem', fontWeight: '600', letterSpacing: '2px', textTransform: 'uppercase'}}>{user?.role || 'USER'}</p>
        <h3 className="user-name" style={{color: 'var(--text-main)', marginTop: '0.5rem'}}> {user?.username || 'Guest'}</h3>
      </div>
      
      <div className="nav-menu">
        <NavLink to="/" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Home size={20} /> Dashboard
        </NavLink>
        <NavLink to="/register" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <UserPlus size={20} /> Register Missing Child
        </NavLink>
        <NavLink to="/search" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <SearchIcon size={20} /> Search / Identify
        </NavLink>
        <NavLink to="/alerts" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
          <Bell size={20} /> Alerts Board
        </NavLink>
        
        {['Admin', 'NGO/Police'].includes(user?.role) && (
          <NavLink to="/cases" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            <Users size={20} /> Manage Cases
          </NavLink>
        )}
      </div>

      <button onClick={onLogout} style={{marginTop: 'auto', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--danger)', padding: '0.8rem', borderRadius: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', transition: 'all 0.2s', fontWeight: '600'}}
      onMouseOver={(e) => { e.currentTarget.style.background = 'var(--danger)'; e.currentTarget.style.color = 'white'; e.currentTarget.style.boxShadow = '0 0 15px rgba(244, 63, 94, 0.4)'; }}
      onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(244, 63, 94, 0.1)'; e.currentTarget.style.color = 'var(--danger)'; e.currentTarget.style.boxShadow = 'none'; }}>
        <LogOut size={20} /> Logout
      </button>
    </aside>
  );
}
