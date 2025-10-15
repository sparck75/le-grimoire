'use client';

import { useState } from 'react';
import Link from 'next/link';
import './admin-global.css';
import './admin.module.css';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="admin-container">
      {/* Mobile Menu Button */}
      <button 
        className="admin-mobile-menu-btn"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        aria-label="Toggle Menu"
      >
        <span className={isSidebarOpen ? 'menu-icon-open' : 'menu-icon'}>☰</span>
      </button>

      {/* Sidebar */}
      <aside className={`admin-sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>Le Grimoire</h2>
          <p className="admin-label">Administration</p>
        </div>
        
        <nav className="admin-nav">
          <Link href="/admin" className="nav-item" onClick={() => setIsSidebarOpen(false)}>
            <span className="nav-icon">📊</span>
            <span>Tableau de Bord</span>
          </Link>
          
          <Link href="/admin/ingredients" className="nav-item" onClick={() => setIsSidebarOpen(false)}>
            <span className="nav-icon">🥕</span>
            <span>Ingrédients</span>
          </Link>
          
          <Link href="/admin/categories" className="nav-item" onClick={() => setIsSidebarOpen(false)}>
            <span className="nav-icon">📁</span>
            <span>Catégories</span>
          </Link>
          
          <Link href="/admin/recipes" className="nav-item" onClick={() => setIsSidebarOpen(false)}>
            <span className="nav-icon">📖</span>
            <span>Recettes</span>
          </Link>
          
          <div className="nav-divider"></div>
          
          <Link href="/" className="nav-item" onClick={() => setIsSidebarOpen(false)}>
            <span className="nav-icon">🏠</span>
            <span>Retour au Site</span>
          </Link>
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div 
          className="admin-sidebar-overlay"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
      
      <main className="admin-main">
        {children}
      </main>
    </div>
  );
}
