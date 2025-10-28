'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Navigation.module.css';

export default function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [itemCount, setItemCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();
  const { user, logout, isAdmin, isCollaborator } = useAuth();

  useEffect(() => {
    // Update item count from localStorage
    const updateCount = () => {
      const stored = localStorage.getItem('shoppingList');
      if (stored) {
        try {
          const items = JSON.parse(stored);
          const unchecked = items.filter((item: any) => !item.checked);
          setItemCount(unchecked.length);
        } catch (e) {
          setItemCount(0);
        }
      } else {
        setItemCount(0);
      }
    };

    updateCount();

    // Listen for storage events (when list is updated from other tabs/pages)
    window.addEventListener('storage', updateCount);
    
    // Custom event for same-page updates
    const handleListUpdate = () => updateCount();
    window.addEventListener('shoppingListUpdated', handleListUpdate);

    return () => {
      window.removeEventListener('storage', updateCount);
      window.removeEventListener('shoppingListUpdated', handleListUpdate);
    };
  }, []);

  // Handle logout
  const handleLogout = async () => {
    await logout();
    setUserMenuOpen(false);
    setIsOpen(false);
    router.push('/');
  };

  // Hide navigation on admin pages (after all hooks)
  if (pathname?.startsWith('/admin')) {
    return null;
  }

  return (
    <>
      {/* Floating Shopping List Button */}
      <Link href="/shopping-list" className={styles.floatingButton}>
        <span className={styles.icon}>🛒</span>
        {itemCount > 0 && (
          <span className={styles.badge}>{itemCount}</span>
        )}
      </Link>

      {/* Mobile Menu Button */}
      <button 
        className={styles.menuButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Menu"
      >
        <span className={isOpen ? styles.menuIconOpen : styles.menuIcon}>☰</span>
      </button>

      {/* Navigation Menu */}
      <nav className={`${styles.nav} ${isOpen ? styles.navOpen : ''}`}>
        <div className={styles.navContent}>
          {/* Logo/Brand - Desktop only */}
          <Link href="/" className={styles.logo} onClick={() => setIsOpen(false)}>
            <span className={styles.logoIcon}>📖</span>
            <span className={styles.logoText}>Le Grimoire</span>
          </Link>

          {/* Navigation Links */}
          <div className={styles.navLinks}>
            <Link 
              href="/" 
              className={pathname === '/' ? styles.navLinkActive : styles.navLink}
              onClick={() => setIsOpen(false)}
            >
              🏠 <span>{t('home')}</span>
            </Link>
            <Link 
              href="/recipes" 
              className={pathname?.startsWith('/recipes') ? styles.navLinkActive : styles.navLink}
              onClick={() => setIsOpen(false)}
            >
              📚 <span>{t('recipes')}</span>
            </Link>
            <Link 
              href="/ingredients" 
              className={pathname === '/ingredients' ? styles.navLinkActive : styles.navLink}
              onClick={() => setIsOpen(false)}
            >
              🥕 <span>{t('ingredients')}</span>
            </Link>
            <Link 
              href="/conversions" 
              className={pathname === '/conversions' ? styles.navLinkActive : styles.navLink}
              onClick={() => setIsOpen(false)}
            >
              🔄 <span>Conversions</span>
            </Link>
            <Link 
              href="/shopping-list" 
              className={pathname === '/shopping-list' ? styles.navLinkActive : styles.navLink}
              onClick={() => setIsOpen(false)}
            >
              🛒 <span>{t('shopping_list')}</span>
              {itemCount > 0 && (
                <span className={styles.navBadge}>{itemCount}</span>
              )}
            </Link>
            
            {/* Show "Add Recipe" for collaborators and admins */}
            {isCollaborator() && (
              <Link 
                href="/recipes/new" 
                className={pathname === '/recipes/new' ? styles.navLinkActive : styles.navLink}
                onClick={() => setIsOpen(false)}
              >
                ➕ <span>Ajouter une Recette</span>
              </Link>
            )}
            
            {/* Show "Admin Panel" for admins only */}
            {isAdmin() && (
              <Link 
                href="/admin" 
                className={pathname?.startsWith('/admin') ? styles.navLinkActive : styles.navLink}
                onClick={() => setIsOpen(false)}
              >
                ⚙️ <span>{t('admin')}</span>
              </Link>
            )}
          </div>

          {/* User Menu or Login Button */}
          {user ? (
            <div className={styles.userMenu}>
              <button 
                className={styles.userButton}
                onClick={() => setUserMenuOpen(!userMenuOpen)}
              >
                <span className={styles.userIcon}>👤</span>
                <span className={styles.userName}>{user.username}</span>
              </button>
              {userMenuOpen && (
                <div className={styles.userDropdown}>
                  <div className={styles.userInfo}>
                    <div className={styles.userEmail}>{user.email}</div>
                    <div className={styles.userRole}>
                      {user.role === 'admin' && '👑 Admin'}
                      {user.role === 'collaborator' && '✍️ Collaborateur'}
                      {user.role === 'reader' && '👀 Lecteur'}
                    </div>
                  </div>
                  <Link 
                    href="/profile" 
                    className={styles.profileButton}
                    onClick={() => {
                      setUserMenuOpen(false);
                      setIsOpen(false);
                    }}
                  >
                    👤 Mon Profil
                  </Link>
                  <button 
                    className={styles.logoutButton}
                    onClick={handleLogout}
                  >
                    🚪 Déconnexion
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link 
              href="/login" 
              className={styles.loginButton}
              onClick={() => setIsOpen(false)}
            >
              🔑 <span>Connexion</span>
            </Link>
          )}

          {/* Language Selector */}
          <div className={styles.languageSelector}>
            <button 
              onClick={() => setLanguage('fr')}
              className={language === 'fr' ? styles.langButtonActive : styles.langButton}
              aria-label="Français"
            >
              🇫🇷
            </button>
            <button 
              onClick={() => setLanguage('en')}
              className={language === 'en' ? styles.langButtonActive : styles.langButton}
              aria-label="English"
            >
              🇺🇸
            </button>
          </div>
        </div>
      </nav>

      {/* Overlay for mobile menu */}
      {isOpen && (
        <div 
          className={styles.overlay}
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
