import React, { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import GlobalPlacePage from './pages/GlobalPlacePage';
import { AuthProvider } from './context/AuthContext';
import AuthModal from './components/AuthModal';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); // 'home' | 'global'
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  useEffect(() => {
    const path = window.location.pathname;
    if (path.includes('/global')) {
      setCurrentPage('global');
    }
  }, []);

  const handleNavigate = (page) => {
    setCurrentPage(page);
    if (page === 'global') {
      window.history.pushState({}, '', '/global');
    } else {
      window.history.pushState({}, '', '/');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectProjectFromGlobal = (projectId) => {
    setSelectedProjectId(projectId);
    setCurrentPage('home');
    window.history.pushState({ projectId }, '', `/?p=${projectId}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <AuthProvider>
      {currentPage === 'global' ? (
        <GlobalPlacePage 
          onSelectProject={handleSelectProjectFromGlobal} 
          onNavigateHome={() => handleNavigate('home')} 
        />
      ) : (
        <HomePage 
          initialProjectId={selectedProjectId}
          onNavigate={handleNavigate}
        />
      )}
      <AuthModal />
    </AuthProvider>
  );
}
