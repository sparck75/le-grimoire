'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';
import styles from './users.module.css';

interface User {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'collaborator' | 'reader';
  is_active: boolean;
  name?: string;
  created_at: string;
}

interface CreateUserForm {
  email: string;
  username: string;
  password: string;
  role: 'admin' | 'collaborator' | 'reader';
  name?: string;
}

export default function AdminUsersPage() {
  const router = useRouter();
  const { user, isAdmin } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [createForm, setCreateForm] = useState<CreateUserForm>({
    email: '',
    username: '',
    password: '',
    role: 'reader',
    name: ''
  });

  // Check if user is admin
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (!isAdmin()) {
      router.push('/');
      return;
    }
  }, [user, isAdmin, router]);

  // Fetch users
  useEffect(() => {
    if (!user || !isAdmin()) return;
    fetchUsers();
  }, [user, isAdmin]);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/admin/users/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/admin/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(createForm)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create user');
      }

      setShowCreateModal(false);
      setCreateForm({
        email: '',
        username: '',
        password: '',
        role: 'reader',
        name: ''
      });
      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    }
  };

  const handleUpdateRole = async (userId: string, newRole: 'admin' | 'collaborator' | 'reader') => {
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/admin/users/${userId}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role: newRole })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update role');
      }

      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update role');
    }
  };

  const handleToggleActive = async (userId: string, currentStatus: boolean) => {
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update user');
      }

      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user');
    }
  };

  const handleDeleteUser = async (userId: string, username: string) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${username}" ?`)) {
      return;
    }

    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete user');
      }

      fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    }
  };

  // Filter users
  const filteredUsers = users.filter(u => {
    const matchesSearch = u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         u.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || u.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return '👑';
      case 'collaborator': return '✍️';
      case 'reader': return '👀';
      default: return '👤';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Admin';
      case 'collaborator': return 'Collaborateur';
      case 'reader': return 'Lecteur';
      default: return role;
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Chargement des utilisateurs...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>👥 Gestion des Utilisateurs</h1>
        <button
          className={styles.createButton}
          onClick={() => setShowCreateModal(true)}
        >
          ➕ Créer un Utilisateur
        </button>
      </div>

      {error && (
        <div className={styles.error}>{error}</div>
      )}

      {/* Filters */}
      <div className={styles.filters}>
        <input
          type="text"
          placeholder="🔍 Rechercher par nom ou email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className={styles.roleFilter}
        >
          <option value="all">Tous les rôles</option>
          <option value="admin">👑 Admin</option>
          <option value="collaborator">✍️ Collaborateur</option>
          <option value="reader">👀 Lecteur</option>
        </select>
      </div>

      {/* Users Table */}
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>Email</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Créé le</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((u) => (
              <tr key={u.id} className={!u.is_active ? styles.inactiveRow : ''}>
                <td>
                  <div className={styles.userCell}>
                    <span className={styles.userIcon}>{getRoleIcon(u.role)}</span>
                    <div>
                      <div className={styles.username}>{u.username}</div>
                      {u.name && <div className={styles.userNameSmall}>{u.name}</div>}
                    </div>
                  </div>
                </td>
                <td>{u.email}</td>
                <td>
                  <select
                    value={u.role}
                    onChange={(e) => handleUpdateRole(u.id, e.target.value as any)}
                    className={styles.roleSelect}
                    disabled={u.id === user?.id}
                  >
                    <option value="admin">👑 Admin</option>
                    <option value="collaborator">✍️ Collaborateur</option>
                    <option value="reader">👀 Lecteur</option>
                  </select>
                </td>
                <td>
                  <button
                    className={u.is_active ? styles.statusActive : styles.statusInactive}
                    onClick={() => handleToggleActive(u.id, u.is_active)}
                    disabled={u.id === user?.id}
                  >
                    {u.is_active ? '✓ Actif' : '✗ Inactif'}
                  </button>
                </td>
                <td>{new Date(u.created_at).toLocaleDateString('fr-FR')}</td>
                <td>
                  <button
                    className={styles.deleteButton}
                    onClick={() => handleDeleteUser(u.id, u.username)}
                    disabled={u.id === user?.id}
                    title="Supprimer l'utilisateur"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredUsers.length === 0 && (
          <div className={styles.emptyState}>
            Aucun utilisateur trouvé
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className={styles.modalOverlay} onClick={() => setShowCreateModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 className={styles.modalTitle}>Créer un Utilisateur</h2>
            <form onSubmit={handleCreateUser} className={styles.form}>
              <div className={styles.formGroup}>
                <label className={styles.label}>Email *</label>
                <input
                  type="email"
                  required
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  className={styles.input}
                  placeholder="utilisateur@example.com"
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Nom d'utilisateur *</label>
                <input
                  type="text"
                  required
                  minLength={3}
                  value={createForm.username}
                  onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                  className={styles.input}
                  placeholder="nomutilisateur"
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Nom complet</label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  className={styles.input}
                  placeholder="Jean Dupont"
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Mot de passe *</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  className={styles.input}
                  placeholder="••••••••"
                />
                <small className={styles.hint}>Minimum 6 caractères</small>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Rôle *</label>
                <select
                  value={createForm.role}
                  onChange={(e) => setCreateForm({ ...createForm, role: e.target.value as any })}
                  className={styles.input}
                >
                  <option value="reader">👀 Lecteur (lecture seule)</option>
                  <option value="collaborator">✍️ Collaborateur (peut créer des recettes)</option>
                  <option value="admin">👑 Admin (accès complet)</option>
                </select>
              </div>

              <div className={styles.modalActions}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className={styles.cancelButton}
                >
                  Annuler
                </button>
                <button type="submit" className={styles.submitButton}>
                  Créer l'Utilisateur
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Total</span>
          <span className={styles.statValue}>{users.length}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>👑 Admins</span>
          <span className={styles.statValue}>{users.filter(u => u.role === 'admin').length}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>✍️ Collaborateurs</span>
          <span className={styles.statValue}>{users.filter(u => u.role === 'collaborator').length}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>👀 Lecteurs</span>
          <span className={styles.statValue}>{users.filter(u => u.role === 'reader').length}</span>
        </div>
      </div>
    </div>
  );
}
