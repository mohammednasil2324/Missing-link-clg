import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RegisterChild from './pages/RegisterChild';
import Search from './pages/Search';
import Alerts from './pages/Alerts';
import Cases from './pages/Cases';
import Sidebar from './components/Sidebar';

const ProtectedRoute = ({ user, allowedRoles, children }) => {
  if (!user) {
    return <Navigate to="/" replace />;
  }
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/search" replace />;
  }
  return children;
};

function App() {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return (saved && saved !== 'undefined') ? JSON.parse(saved) : null;
    } catch (e) {
      localStorage.removeItem('user');
      return null;
    }
  });

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-layout">
      <Sidebar user={user} onLogout={handleLogout} />
      <div className="main-content">
        <Routes>
          <Route path="/" element={
            <ProtectedRoute user={user} allowedRoles={['Admin', 'NGO/Police']}>
              <Dashboard user={user} />
            </ProtectedRoute>
          } />
          <Route path="/register" element={<RegisterChild />} />
          <Route path="/search" element={<Search />} />
          <Route path="/alerts" element={
            <ProtectedRoute user={user} allowedRoles={['Admin', 'NGO/Police']}>
              <Alerts />
            </ProtectedRoute>
          } />
          <Route path="/cases" element={
            <ProtectedRoute user={user} allowedRoles={['Admin', 'NGO/Police']}>
              <Cases />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/search" />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
