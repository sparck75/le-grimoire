import Link from 'next/link';
import './admin-global.css';
import './admin.module.css';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="admin-container">
      <aside className="admin-sidebar">
        <div className="sidebar-header">
          <h2>Le Grimoire</h2>
          <p className="admin-label">Administration</p>
        </div>
        
        <nav className="admin-nav">
          <Link href="/admin" className="nav-item">
            <span className="nav-icon">📊</span>
            <span>Tableau de Bord</span>
          </Link>
          
          <Link href="/admin/ingredients" className="nav-item">
            <span className="nav-icon">🥕</span>
            <span>Ingrédients</span>
          </Link>
          
          <Link href="/admin/categories" className="nav-item">
            <span className="nav-icon">📁</span>
            <span>Catégories</span>
          </Link>
          
          <Link href="/admin/recipes" className="nav-item">
            <span className="nav-icon">📖</span>
            <span>Recettes</span>
          </Link>
          
          <div className="nav-divider"></div>
          
          <Link href="/" className="nav-item">
            <span className="nav-icon">🏠</span>
            <span>Retour au Site</span>
          </Link>
        </nav>
      </aside>
      
      <main className="admin-main">
        {children}
      </main>
    </div>
  );
}
