import { NavLink } from 'react-router-dom';
import { Home, UserPlus, Search as SearchIcon, Bell, Users, LogOut } from 'lucide-react';

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <p className="role-badge">ROLE: {user?.role?.toUpperCase() || 'USER'}</p>
        <h3 className="user-name">Logged in as: {user?.username || 'Guest'}</h3>
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

      <button onClick={onLogout} style={{marginTop: 'auto', background: 'transparent', border: '1px solid var(--border-light)', color: 'var(--text-muted)', padding: '0.8rem', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center'}}>
        <LogOut size={20} /> Logout
      </button>
    </aside>
  );
}
