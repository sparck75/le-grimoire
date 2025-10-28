# Guide Rapide - Sauvegarde et Restauration

Guide de référence rapide pour les opérations de sauvegarde et restauration.

## 🚀 Démarrage Rapide

### Production → Dev en 3 étapes

```bash
# 1. Sur le serveur de production : créer une sauvegarde
ssh legrimoire@prod-server
cd ~/apps/le-grimoire
./scripts/backup-production.sh

# 2. Sur votre machine locale : télécharger la sauvegarde
scp legrimoire@prod-server:~/apps/le-grimoire/backups/backup_*.tar.gz ./backups/

# 3. En local : restaurer la sauvegarde
cd /path/to/le-grimoire
docker-compose up -d  # Si pas encore démarré
./scripts/restore-backup.sh backups/backup_*.tar.gz
```

## 📋 Commandes Essentielles

### Sauvegarde

```bash
# Sauvegarde complète
./scripts/backup-production.sh

# Avec configuration personnalisée
BACKUP_RETENTION_DAYS=30 ./scripts/backup-production.sh

# Vérifier les sauvegardes
ls -lh backups/backup_*.tar.gz
```

### Restauration

```bash
# Restaurer une sauvegarde complète
./scripts/restore-backup.sh backup_20251028_143022.tar.gz

# Lister les sauvegardes disponibles
./scripts/restore-backup.sh
```

### Vérification

```bash
# MongoDB
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --eval "
  use legrimoire;
  print('Recipes:', db.recipes.countDocuments());
  print('Ingredients:', db.ingredients.countDocuments());
"

# PostgreSQL
docker-compose exec db psql -U grimoire -d le_grimoire -c "SELECT COUNT(*) FROM recipes;"

# API
curl http://localhost:8000/api/health
```

## 🔧 Opérations Courantes

### Sauvegarde MongoDB uniquement

```bash
docker-compose exec mongodb mongodump \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin" \
  --out=/tmp/dump

docker cp le-grimoire-mongodb:/tmp/dump ./backups/mongodb_$(date +%Y%m%d)
```

### Restaurer MongoDB uniquement

```bash
# Extraire d'abord la sauvegarde si nécessaire
tar -xzf backups/backup_20251028_143022.tar.gz

# Restaurer
docker cp backup_20251028_143022/mongodb le-grimoire-mongodb:/tmp/restore
docker-compose exec mongodb mongorestore \
  --uri="mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin" \
  --drop \
  /tmp/restore
```

### Nettoyer et repartir à zéro

```bash
# ⚠️  ATTENTION: Supprime toutes les données locales!
docker-compose down -v
docker-compose up -d
sleep 30
./scripts/restore-backup.sh backups/backup_latest.tar.gz
```

## 📊 Surveillance

### Taille des sauvegardes

```bash
du -h backups/*.tar.gz | tail -5
```

### Dernière sauvegarde

```bash
ls -lt backups/backup_*.tar.gz | head -1
```

### Nombre de documents

```bash
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password --eval "
  use legrimoire;
  db.getCollectionNames().forEach(function(col) {
    print(col + ':', db[col].countDocuments());
  });
"
```

## ⏰ Automatisation (Production)

### Configuration Cron

```bash
# Éditer crontab
crontab -e

# Sauvegarde quotidienne à 2h du matin
0 2 * * * cd ~/apps/le-grimoire && ./scripts/backup-production.sh >> ~/logs/backup.log 2>&1
```

### Vérifier le cron

```bash
# Voir les tâches planifiées
crontab -l

# Voir le log des sauvegardes
tail -f ~/logs/backup.log
```

## 🚨 Dépannage Rapide

### Erreur d'authentification MongoDB

```bash
# Vérifier les variables d'environnement
docker-compose exec mongodb env | grep MONGO

# Tester la connexion
docker-compose exec mongodb mongosh -u legrimoire -p grimoire_mongo_password
```

### Conteneur ne démarre pas

```bash
# Voir les logs
docker-compose logs mongodb

# Redémarrer
docker-compose restart mongodb

# Recréer si nécessaire
docker-compose up -d --force-recreate mongodb
```

### Sauvegarde corrompue

```bash
# Vérifier l'intégrité
tar -tzf backups/backup_20251028_143022.tar.gz > /dev/null && echo "OK" || echo "CORRUPTED"

# Extraire pour inspection
tar -xzf backups/backup_20251028_143022.tar.gz
cat backup_20251028_143022/backup_info.txt
```

### Espace disque plein

```bash
# Vérifier l'espace
df -h

# Nettoyer les anciennes sauvegardes (> 30 jours)
find backups/ -name "backup_*.tar.gz" -mtime +30 -delete

# Compresser davantage
for f in backups/*.tar.gz; do
  gzip -d "$f" && xz -9 "${f%.gz}"
done
```

## 📚 Plus d'informations

- Documentation complète : [docs/operations/BACKUP_RESTORE.md](./BACKUP_RESTORE.md)
- Déploiement : [docs/deployment/DEPLOYMENT_OVERVIEW.md](../deployment/DEPLOYMENT_OVERVIEW.md)
- Dépannage : [docs/deployment/TROUBLESHOOTING.md](../deployment/TROUBLESHOOTING.md)

## 💡 Bonnes Pratiques

1. **Testez régulièrement** vos restaurations
2. **Gardez au moins 7 jours** de sauvegardes
3. **Vérifiez l'intégrité** après chaque sauvegarde
4. **Stockez hors site** les sauvegardes importantes
5. **Documentez** toute personnalisation
6. **Automatisez** les sauvegardes en production

---

Pour plus de détails, consultez [BACKUP_RESTORE.md](./BACKUP_RESTORE.md)
