# Guide de Sauvegarde et Restauration - Le Grimoire

Ce guide détaille les procédures complètes de sauvegarde et restauration pour synchroniser les bases de données de production vers le développement.

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Sauvegarde de Production](#sauvegarde-de-production)
3. [Restauration en Développement](#restauration-en-développement)
4. [Sauvegardes Automatisées](#sauvegardes-automatisées)
5. [Dépannage](#dépannage)

## 🎯 Vue d'ensemble

Le système de sauvegarde et restauration permet de :

- ✅ Créer des sauvegardes complètes de la production (MongoDB, PostgreSQL, fichiers)
- ✅ Restaurer ces sauvegardes en développement pour avoir un environnement identique
- ✅ Valider automatiquement les bases de données au démarrage des conteneurs
- ✅ Planifier des sauvegardes automatiques avec rétention configurable
- ✅ Exporter/importer les données en JSON pour une portabilité maximale

### Architecture des Sauvegardes

```
backup_YYYYMMDD_HHMMSS/
├── backup_info.txt                 # Métadonnées de sauvegarde
├── mongodb/                        # Dump MongoDB (BSON)
│   ├── legrimoire/
│   │   ├── recipes.bson
│   │   ├── recipes.metadata.json
│   │   ├── ingredients.bson
│   │   ├── ingredients.metadata.json
│   │   └── categories.bson
├── postgresql/                     # Dump PostgreSQL
│   ├── database.backup            # Format custom (pg_restore)
│   └── database.sql               # Format SQL (lisible)
├── uploads/                        # Fichiers uploadés
│   └── [images de recettes]
├── recipes_export.json             # Export JSON des recettes
└── ingredients_export.json         # Export JSON des ingrédients
```

## 🔐 Sauvegarde de Production

### Méthode 1 : Sauvegarde manuelle complète

Sur le **serveur de production** :

```bash
# Se connecter au serveur
ssh legrimoire@your-production-server

# Aller dans le répertoire de l'application
cd ~/apps/le-grimoire

# Lancer la sauvegarde
./scripts/backup-production.sh
```

La sauvegarde créera un fichier compressé dans `backups/backup_YYYYMMDD_HHMMSS.tar.gz`

#### Ce qui est sauvegardé

1. **MongoDB** (base de données principale)
   - Toutes les collections (recipes, ingredients, categories)
   - Indexes et métadonnées
   - Export JSON pour portabilité

2. **PostgreSQL** (legacy - optionnel)
   - Schéma et données
   - Format custom + SQL

3. **Fichiers uploadés**
   - Images de recettes
   - Fichiers OCR

4. **Métadonnées**
   - Date et heure de sauvegarde
   - Environnement
   - Instructions de restauration

### Méthode 2 : Sauvegarde avec variables personnalisées

```bash
# Sauvegarder dans un répertoire spécifique
BACKUP_DIR=/custom/path ./scripts/backup-production.sh

# Modifier la rétention des sauvegardes (défaut: 7 jours)
BACKUP_RETENTION_DAYS=30 ./scripts/backup-production.sh

# Spécifier les conteneurs Docker (si noms différents)
MONGODB_CONTAINER=my-mongodb \
POSTGRES_CONTAINER=my-postgres \
./scripts/backup-production.sh
```

### Télécharger la Sauvegarde

Depuis votre **machine locale** :

```bash
# Télécharger la dernière sauvegarde
scp legrimoire@your-production-server:~/apps/le-grimoire/backups/backup_*.tar.gz ./backups/

# Ou spécifier une sauvegarde précise
scp legrimoire@your-production-server:~/apps/le-grimoire/backups/backup_20251028_143022.tar.gz ./backups/
```

### Vérifier une Sauvegarde

```bash
# Lister le contenu sans extraire
tar -tzf backups/backup_20251028_143022.tar.gz | head -20

# Voir les informations de la sauvegarde
tar -xzf backups/backup_20251028_143022.tar.gz backup_20251028_143022/backup_info.txt -O
```

## 🔄 Restauration en Développement

### Prérequis

1. Avoir téléchargé une sauvegarde de production
2. Les conteneurs Docker doivent être démarrés
3. Avoir les permissions nécessaires

### Étape 1 : Préparer l'Environnement

```bash
# Aller dans le répertoire du projet
cd /path/to/le-grimoire

# Démarrer les conteneurs si nécessaire
docker-compose up -d

# Attendre que les bases de données soient prêtes (30 secondes environ)
docker-compose logs -f mongodb
# Appuyez sur Ctrl+C quand vous voyez "MongoDB initialization complete"
```

### Étape 2 : Restaurer la Sauvegarde

```bash
# Restaurer une sauvegarde compressée
./scripts/restore-backup.sh backup_20251028_143022.tar.gz

# Ou restaurer depuis un répertoire déjà extrait
./scripts/restore-backup.sh backup_20251028_143022
```

Le script va :
1. ✅ Extraire la sauvegarde si nécessaire
2. ✅ Afficher les informations de la sauvegarde
3. ✅ Demander confirmation (tape 'yes')
4. ✅ Restaurer MongoDB (avec --drop pour nettoyer avant)
5. ✅ Restaurer PostgreSQL (si présent)
6. ✅ Copier les fichiers uploadés
7. ✅ Vérifier que tout est bien restauré
8. ✅ Afficher les statistiques

### Étape 3 : Vérifier la Restauration

```bash
# Vérifier MongoDB
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --authenticationDatabase admin

# Dans mongosh
use legrimoire
db.recipes.countDocuments()
db.ingredients.countDocuments()
db.categories.countDocuments()
exit

# Vérifier PostgreSQL (si utilisé)
docker-compose exec db psql -U grimoire -d le_grimoire -c "SELECT COUNT(*) FROM recipes;"

# Vérifier l'application
open http://localhost:3000
# Ou
curl http://localhost:8000/api/health
```

### Restauration Partielle

Si vous voulez restaurer seulement certains composants :

#### MongoDB uniquement

```bash
# Extraire la sauvegarde
tar -xzf backups/backup_20251028_143022.tar.gz

# Restaurer MongoDB
docker-compose exec -T mongodb mongorestore \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin" \
  --drop \
  < backup_20251028_143022/mongodb/

# Ou copier dans le conteneur puis restaurer
docker cp backup_20251028_143022/mongodb/ le-grimoire-mongodb:/tmp/restore/
docker-compose exec mongodb mongorestore \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin" \
  --drop \
  /tmp/restore/
```

#### PostgreSQL uniquement

```bash
# Restaurer depuis le format custom
docker cp backup_20251028_143022/postgresql/database.backup le-grimoire-db:/tmp/
docker-compose exec db pg_restore \
  -U grimoire \
  -d le_grimoire \
  --clean \
  /tmp/database.backup

# Ou depuis le SQL
docker cp backup_20251028_143022/postgresql/database.sql le-grimoire-db:/tmp/
docker-compose exec db psql -U grimoire -d le_grimoire -f /tmp/database.sql
```

#### Fichiers uploadés uniquement

```bash
docker cp backup_20251028_143022/uploads/. le-grimoire-backend:/app/uploads/
```

#### Depuis les exports JSON

```bash
# Copier les fichiers JSON dans le conteneur backend
docker cp backup_20251028_143022/recipes_export.json le-grimoire-backend:/app/data/
docker cp backup_20251028_143022/ingredients_export.json le-grimoire-backend:/app/data/

# Importer les recettes
docker-compose exec backend python scripts/import_recipes_from_json.py /app/data/recipes_export.json

# Importer les ingrédients
docker-compose exec backend python scripts/import_off_ingredients.py /app/data/ingredients_export.json
```

## ⏰ Sauvegardes Automatisées

### Configuration sur le Serveur de Production

#### Méthode 1 : Cron (Linux)

```bash
# Éditer le crontab de l'utilisateur legrimoire
crontab -e

# Ajouter une sauvegarde quotidienne à 2h du matin
0 2 * * * cd ~/apps/le-grimoire && ./scripts/backup-production.sh >> ~/logs/backup.log 2>&1

# Ou une sauvegarde toutes les 6 heures
0 */6 * * * cd ~/apps/le-grimoire && ./scripts/backup-production.sh >> ~/logs/backup.log 2>&1

# Ou deux fois par jour (2h et 14h)
0 2,14 * * * cd ~/apps/le-grimoire && ./scripts/backup-production.sh >> ~/logs/backup.log 2>&1
```

#### Méthode 2 : Systemd Timer (recommandé pour production)

Créer `/etc/systemd/system/legrimoire-backup.service` :

```ini
[Unit]
Description=Le Grimoire Database Backup
After=docker.service

[Service]
Type=oneshot
User=legrimoire
WorkingDirectory=/home/legrimoire/apps/le-grimoire
Environment=BACKUP_RETENTION_DAYS=30
ExecStart=/home/legrimoire/apps/le-grimoire/scripts/backup-production.sh
StandardOutput=append:/home/legrimoire/logs/backup.log
StandardError=append:/home/legrimoire/logs/backup-error.log
```

Créer `/etc/systemd/system/legrimoire-backup.timer` :

```ini
[Unit]
Description=Le Grimoire Backup Timer
Requires=legrimoire-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Activer et démarrer :

```bash
sudo systemctl daemon-reload
sudo systemctl enable legrimoire-backup.timer
sudo systemctl start legrimoire-backup.timer

# Vérifier le status
sudo systemctl status legrimoire-backup.timer
sudo systemctl list-timers | grep legrimoire
```

### Configuration de la Rétention

Par défaut, les sauvegardes sont conservées 7 jours. Pour modifier :

```bash
# Dans .env.production
BACKUP_RETENTION_DAYS=30

# Ou en variable d'environnement dans le cron/systemd
```

### Surveillance des Sauvegardes

Créer un script de surveillance `/home/legrimoire/apps/le-grimoire/scripts/check-backups.sh` :

```bash
#!/bin/bash

BACKUP_DIR="/home/legrimoire/apps/le-grimoire/backups"
MAX_AGE_HOURS=26  # Alerte si dernière sauvegarde > 26h

LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup_*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ ALERT: No backups found in $BACKUP_DIR"
    exit 1
fi

BACKUP_AGE=$(( ($(date +%s) - $(stat -c %Y "$LATEST_BACKUP")) / 3600 ))

if [ $BACKUP_AGE -gt $MAX_AGE_HOURS ]; then
    echo "⚠️  WARNING: Latest backup is $BACKUP_AGE hours old"
    echo "   File: $LATEST_BACKUP"
    exit 1
else
    echo "✅ Latest backup is $BACKUP_AGE hours old"
    echo "   File: $(basename $LATEST_BACKUP)"
    echo "   Size: $(du -h $LATEST_BACKUP | cut -f1)"
fi
```

## 🔧 Validation au Démarrage

Les conteneurs MongoDB vérifient automatiquement au démarrage si les collections et indexes existent.

### Script d'Initialisation MongoDB

Le script `backend/scripts/mongodb/init-db.sh` :

1. ✅ Vérifie la connexion MongoDB
2. ✅ Vérifie l'existence des collections
3. ✅ Crée les indexes nécessaires
4. ✅ Affiche les statistiques

Le script est exécuté automatiquement via `docker-entrypoint-initdb.d/` lors de la première création du conteneur.

### Forcer la Validation

```bash
# Exécuter manuellement la validation
docker-compose exec mongodb /docker-entrypoint-initdb.d/init-db.sh

# Vérifier les indexes
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --authenticationDatabase admin

use legrimoire
db.recipes.getIndexes()
db.ingredients.getIndexes()
db.categories.getIndexes()
```

## 🚨 Dépannage

### Problème : Erreur d'authentification MongoDB

```bash
# Vérifier les credentials dans .env
grep MONGODB .env

# Tester la connexion
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --authenticationDatabase admin

# Si erreur, recréer l'utilisateur
docker-compose exec mongodb mongosh --eval "
  use admin
  db.createUser({
    user: 'legrimoire',
    pwd: 'grimoire_mongo_password',
    roles: [{role: 'root', db: 'admin'}]
  })
"
```

### Problème : Conteneur ne démarre pas après restauration

```bash
# Vérifier les logs
docker-compose logs mongodb
docker-compose logs backend

# Redémarrer les conteneurs
docker-compose restart

# Si problème persiste, recréer
docker-compose down
docker-compose up -d
```

### Problème : Sauvegarde trop volumineuse

```bash
# Sauvegarder seulement MongoDB (pas de PostgreSQL)
docker-compose exec mongodb mongodump \
  --out /tmp/dump \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin"

docker cp le-grimoire-mongodb:/tmp/dump ./backups/manual_dump_$(date +%Y%m%d)

# Compresser avec meilleure compression
tar -czf backups/manual_$(date +%Y%m%d).tar.gz -C backups manual_dump_*
```

### Problème : Restauration échoue avec "collection already exists"

```bash
# Utiliser l'option --drop pour remplacer les collections
docker-compose exec mongodb mongorestore \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin" \
  --drop \
  /path/to/backup/

# Ou supprimer manuellement avant
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --authenticationDatabase admin
use legrimoire
db.recipes.drop()
db.ingredients.drop()
db.categories.drop()
exit
```

### Problème : Permissions sur les fichiers restaurés

```bash
# Corriger les permissions dans le conteneur
docker-compose exec backend chown -R app:app /app/uploads/
docker-compose exec backend chmod -R 755 /app/uploads/
```

## 📝 Checklist de Restauration Complète

Suivre cette checklist pour restaurer une copie complète de production en développement :

- [ ] 1. Télécharger la dernière sauvegarde de production
  ```bash
  scp legrimoire@prod:~/apps/le-grimoire/backups/backup_latest.tar.gz ./backups/
  ```

- [ ] 2. Arrêter l'application locale si nécessaire
  ```bash
  docker-compose down
  ```

- [ ] 3. Nettoyer les volumes (ATTENTION: supprime toutes les données)
  ```bash
  docker volume rm le-grimoire_mongodb_data le-grimoire_postgres_data
  ```

- [ ] 4. Démarrer les conteneurs
  ```bash
  docker-compose up -d
  sleep 30  # Attendre l'initialisation
  ```

- [ ] 5. Restaurer la sauvegarde
  ```bash
  ./scripts/restore-backup.sh backup_latest.tar.gz
  ```

- [ ] 6. Vérifier les données
  ```bash
  # MongoDB
  docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --eval "
    use legrimoire;
    print('Recipes:', db.recipes.countDocuments());
    print('Ingredients:', db.ingredients.countDocuments());
  "
  
  # Application web
  open http://localhost:3000
  ```

- [ ] 7. Tester les fonctionnalités critiques
  - [ ] Affichage des recettes
  - [ ] Recherche d'ingrédients
  - [ ] Création de recette
  - [ ] Upload d'image

- [ ] 8. Ajuster les configurations pour le développement
  ```bash
  # Mettre NEXT_PUBLIC_API_URL à localhost
  # Dans .env
  NEXT_PUBLIC_API_URL=http://localhost:8000
  
  # Reconstruire le frontend si nécessaire
  docker-compose restart frontend
  ```

## 📚 Ressources Supplémentaires

- [Documentation MongoDB Backup](https://www.mongodb.com/docs/manual/core/backups/)
- [Documentation PostgreSQL Backup](https://www.postgresql.org/docs/current/backup.html)
- [Guide Docker Compose](https://docs.docker.com/compose/)
- [Guide de Déploiement](../deployment/DEPLOYMENT_OVERVIEW.md)
- [Dépannage](../deployment/TROUBLESHOOTING.md)

## 🔐 Bonnes Pratiques de Sécurité

1. **Sauvegardes**
   - Ne jamais committer les sauvegardes dans Git
   - Chiffrer les sauvegardes si elles contiennent des données sensibles
   - Stocker les sauvegardes dans un emplacement sécurisé hors serveur

2. **Credentials**
   - Ne jamais mettre les mots de passe dans les scripts
   - Utiliser des variables d'environnement
   - Différencier les credentials prod/dev

3. **Transferts**
   - Utiliser SCP ou SFTP (pas FTP)
   - Vérifier les checksums après transfert
   - Supprimer les fichiers temporaires après utilisation

4. **Accès**
   - Limiter l'accès aux scripts de sauvegarde
   - Logger toutes les opérations de backup/restore
   - Tester régulièrement les restaurations

## 💡 Conseils

- **Testez régulièrement** vos procédures de restauration
- **Documentez** tout changement dans la structure des données
- **Gardez** plusieurs générations de sauvegardes
- **Vérifiez** l'intégrité des sauvegardes après création
- **Automatisez** au maximum pour éviter les erreurs humaines
- **Surveillez** l'espace disque des sauvegardes

---

**Dernière mise à jour** : 28 octobre 2025  
**Version** : 1.0.0
