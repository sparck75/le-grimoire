'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import styles from './profile.module.css';

export default function ProfilePage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  
  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Redirect if not logged in
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.profileCard}>
          <div className={styles.header}>
            <h1 className={styles.title}>Chargement...</h1>
          </div>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!user) {
    return null;
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setPasswordError('Les nouveaux mots de passe ne correspondent pas');
      return;
    }

    // Validate password length
    if (newPassword.length < 6) {
      setPasswordError('Le nouveau mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setPasswordLoading(true);

    try {
      const response = await fetch('/api/auth/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }

      const data = await response.json();
      setPasswordSuccess(data.message);
      
      // Clear form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setPasswordLoading(false);
    }
  };

  const getRoleBadge = () => {
    switch (user.role) {
      case 'admin':
        return { icon: '👑', text: 'Administrateur', color: '#ff6b6b' };
      case 'collaborator':
        return { icon: '✍️', text: 'Collaborateur', color: '#4ecdc4' };
      case 'reader':
        return { icon: '👀', text: 'Lecteur', color: '#95a5a6' };
      default:
        return { icon: '👤', text: 'Utilisateur', color: '#95a5a6' };
    }
  };

  const roleBadge = getRoleBadge();

  return (
    <div className={styles.container}>
      <div className={styles.profileCard}>
        <div className={styles.header}>
          <h1 className={styles.title}>Mon Profil</h1>
          <p className={styles.subtitle}>Gérez vos informations personnelles</p>
        </div>

        {/* User Information Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Informations du compte</h2>
          
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>Nom d'utilisateur</div>
              <div className={styles.infoValue}>{user.username}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>Email</div>
              <div className={styles.infoValue}>{user.email}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>Rôle</div>
              <div className={styles.infoValue}>
                <span 
                  className={styles.roleBadge}
                  style={{ backgroundColor: roleBadge.color }}
                >
                  {roleBadge.icon} {roleBadge.text}
                </span>
              </div>
            </div>

            {user.name && (
              <div className={styles.infoItem}>
                <div className={styles.infoLabel}>Nom complet</div>
                <div className={styles.infoValue}>{user.name}</div>
              </div>
            )}
          </div>
        </div>

        {/* Password Change Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Changer le mot de passe</h2>
          
          <form onSubmit={handlePasswordChange} className={styles.form}>
            {passwordError && (
              <div className={styles.error}>
                {passwordError}
              </div>
            )}
            
            {passwordSuccess && (
              <div className={styles.success}>
                {passwordSuccess}
              </div>
            )}

            <div className={styles.formGroup}>
              <label htmlFor="currentPassword" className={styles.label}>
                Mot de passe actuel
              </label>
              <input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className={styles.input}
                required
                autoComplete="current-password"
                disabled={passwordLoading}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="newPassword" className={styles.label}>
                Nouveau mot de passe
              </label>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className={styles.input}
                required
                autoComplete="new-password"
                disabled={passwordLoading}
                minLength={6}
              />
              <div className={styles.hint}>
                Minimum 6 caractères
              </div>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="confirmPassword" className={styles.label}>
                Confirmer le nouveau mot de passe
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={styles.input}
                required
                autoComplete="new-password"
                disabled={passwordLoading}
                minLength={6}
              />
            </div>

            <button
              type="submit"
              className={styles.submitButton}
              disabled={passwordLoading}
            >
              {passwordLoading ? 'Modification...' : 'Changer le mot de passe'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
