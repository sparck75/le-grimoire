# Documentation Opérationnelle - Le Grimoire

Documentation pour les opérations quotidiennes, la maintenance et la gestion des bases de données.

## 📚 Guides Disponibles

### [Guide de Sauvegarde et Restauration](./BACKUP_RESTORE.md)
Documentation complète pour la synchronisation des bases de données entre production et développement.

**Contenu** :
- 🔐 Procédures de sauvegarde de production
- 🔄 Restauration en développement
- ⏰ Configuration des sauvegardes automatisées
- 🚨 Dépannage et résolution de problèmes
- 📝 Checklists de validation

**Utilisez ce guide si** :
- Vous devez créer un environnement de développement identique à la production
- Vous voulez mettre en place des sauvegardes automatiques
- Vous devez récupérer des données après un incident
- Vous migrez vers un nouveau serveur

### [Guide de Démarrage Rapide](./QUICKSTART.md)
Référence rapide pour les commandes courantes de sauvegarde et restauration.

**Contenu** :
- 🚀 Commandes essentielles
- 📋 Opérations courantes
- 🔧 Dépannage rapide
- ⏰ Configuration cron

**Utilisez ce guide si** :
- Vous connaissez déjà les procédures et avez besoin d'un rappel rapide
- Vous cherchez une commande spécifique
- Vous voulez un aide-mémoire pour les opérations courantes

## 🎯 Parcours Recommandés

### Pour les Nouveaux Utilisateurs

1. **Lisez d'abord** : [BACKUP_RESTORE.md](./BACKUP_RESTORE.md) - Sections "Vue d'ensemble" et "Architecture"
2. **Suivez** : [BACKUP_RESTORE.md](./BACKUP_RESTORE.md) - Section "Restauration en Développement" avec une vraie sauvegarde
3. **Gardez sous la main** : [QUICKSTART.md](./QUICKSTART.md) pour les commandes courantes

### Pour les Administrateurs Système

1. **Configurez** : [BACKUP_RESTORE.md](./BACKUP_RESTORE.md) - Section "Sauvegardes Automatisées"
2. **Surveillez** : [BACKUP_RESTORE.md](./BACKUP_RESTORE.md) - Section "Surveillance des Sauvegardes"
3. **Testez régulièrement** : Procédures de restauration pour validation

### Pour les Développeurs

1. **Synchronisez** : [QUICKSTART.md](./QUICKSTART.md) - "Production → Dev en 3 étapes"
2. **Vérifiez** : [QUICKSTART.md](./QUICKSTART.md) - Section "Vérification"
3. **Dépannez** : [BACKUP_RESTORE.md](./BACKUP_RESTORE.md) - Section "Dépannage"

## 🛠️ Scripts Disponibles

Tous les scripts sont situés dans `/scripts/` :

### `backup-production.sh`
Crée une sauvegarde complète de la production (MongoDB, PostgreSQL, uploads).

```bash
./scripts/backup-production.sh
```

**Variables d'environnement** :
- `BACKUP_DIR` : Répertoire de destination (défaut: `./backups`)
- `BACKUP_RETENTION_DAYS` : Jours de rétention (défaut: 7)
- `MONGODB_CONTAINER` : Nom du conteneur MongoDB
- `POSTGRES_CONTAINER` : Nom du conteneur PostgreSQL

### `restore-backup.sh`
Restaure une sauvegarde sur l'environnement local.

```bash
./scripts/restore-backup.sh backup_20251028_143022.tar.gz
```

**Fonctionnalités** :
- ✅ Extraction automatique des archives
- ✅ Validation de la structure de sauvegarde
- ✅ Confirmation avant écrasement
- ✅ Vérification post-restauration
- ✅ Nettoyage optionnel

### `backend/scripts/mongodb/init-db.sh`
Initialise et valide la base MongoDB au démarrage du conteneur.

**Exécution automatique** : Via `docker-entrypoint-initdb.d/`

**Vérifications** :
- ✅ Connexion MongoDB
- ✅ Existence des collections
- ✅ Création des indexes
- ✅ Statistiques

## 📊 Structure des Sauvegardes

```
backups/
├── backup_20251028_143022.tar.gz    # Archive complète
├── backup_20251027_020000.tar.gz    # Archive précédente
└── backup_20251026_020000.tar.gz    # Archive plus ancienne

Contenu d'une archive :
backup_20251028_143022/
├── backup_info.txt              # Métadonnées
├── mongodb/                     # Dump BSON
│   └── legrimoire/
│       ├── recipes.bson
│       ├── ingredients.bson
│       └── categories.bson
├── postgresql/                  # Dump PostgreSQL
│   ├── database.backup
│   └── database.sql
├── uploads/                     # Fichiers uploadés
├── recipes_export.json          # Export JSON
└── ingredients_export.json      # Export JSON
```

## 🔐 Sécurité

### Permissions Recommandées

```bash
# Scripts
chmod 750 scripts/*.sh
chown legrimoire:legrimoire scripts/*.sh

# Répertoire de sauvegarde
chmod 700 backups/
chown legrimoire:legrimoire backups/

# Archives
chmod 600 backups/*.tar.gz
```

### Bonnes Pratiques

1. **Ne jamais committer** les sauvegardes dans Git
2. **Chiffrer** les sauvegardes contenant des données sensibles
3. **Stocker hors site** les sauvegardes importantes
4. **Tester régulièrement** les procédures de restauration
5. **Documenter** toute modification des procédures
6. **Limiter l'accès** aux scripts et sauvegardes

### Chiffrement (Optionnel)

```bash
# Chiffrer une sauvegarde avec GPG
gpg --symmetric --cipher-algo AES256 backup_20251028_143022.tar.gz

# Déchiffrer
gpg --decrypt backup_20251028_143022.tar.gz.gpg > backup_20251028_143022.tar.gz
```

## 📈 Monitoring et Alertes

### Vérifier l'Âge des Sauvegardes

```bash
# Dernière sauvegarde
ls -lt backups/backup_*.tar.gz | head -1

# Âge de la dernière sauvegarde
find backups/ -name "backup_*.tar.gz" -mtime -1 | wc -l  # Doit être > 0
```

### Notifications par Email (Optionnel)

Ajouter à la fin de `backup-production.sh` :

```bash
# Envoyer notification de succès
echo "Backup completed: backup_${DATE}.tar.gz ($backup_size)" | \
  mail -s "Le Grimoire Backup Success" admin@example.com
```

### Intégration Monitoring

```bash
# Healthcheck pour monitoring externe (ex: Prometheus)
# Créer /healthcheck/backup-status
echo "backup_last_success_timestamp $(stat -c %Y backups/backup_*.tar.gz | tail -1)" > /var/lib/prometheus/backup-status.prom
```

## 🔗 Ressources Complémentaires

### Documentation Interne
- [Architecture](../architecture/OVERVIEW.md)
- [API Reference](../architecture/API_REFERENCE.md)
- [Déploiement](../deployment/DEPLOYMENT_OVERVIEW.md)
- [Dépannage](../deployment/TROUBLESHOOTING.md)

### Documentation Externe
- [MongoDB Backup](https://www.mongodb.com/docs/manual/core/backups/)
- [PostgreSQL Backup](https://www.postgresql.org/docs/current/backup.html)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)

## 🆘 Support

### En Cas de Problème

1. **Consultez** : [Section Dépannage](./BACKUP_RESTORE.md#dépannage)
2. **Vérifiez les logs** :
   ```bash
   docker-compose logs -f mongodb
   docker-compose logs -f backend
   ```
3. **Ouvrez une issue** : [GitHub Issues](https://github.com/sparck75/le-grimoire/issues)

### Informations Utiles pour le Support

```bash
# Version Docker
docker --version
docker-compose --version

# État des conteneurs
docker-compose ps

# Taille des volumes
docker system df -v | grep le-grimoire

# Dernière sauvegarde
ls -lh backups/backup_*.tar.gz | tail -1
```

---

**Dernière mise à jour** : 28 octobre 2025  
**Mainteneur** : Équipe Le Grimoire
