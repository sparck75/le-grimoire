# Aide-mémoire de déploiement - Le Grimoire

Guide de référence rapide pour les commandes les plus courantes en production.

## 📦 Déploiement

```bash
# Déploiement initial
./deploy.sh deploy

# Mise à jour
./deploy.sh update
```

## 🔄 Gestion des services

```bash
# Démarrer
docker compose -f docker-compose.prod.yml up -d

# Arrêter
docker compose -f docker-compose.prod.yml down

# Redémarrer
docker compose -f docker-compose.prod.yml restart

# Redémarrer un service spécifique
docker compose -f docker-compose.prod.yml restart nginx
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart frontend
```

## 📊 Monitoring

```bash
# Statut des conteneurs
docker compose -f docker-compose.prod.yml ps

# Logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Logs d'un service
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs mongodb

# Utilisation des ressources
docker stats

# Espace disque
df -h

# Utilisation RAM
free -h
```

## 💾 Sauvegardes

```bash
# Sauvegarde manuelle
./deploy.sh backup

# Lister les sauvegardes
ls -lh backups/

# Nettoyer les anciennes sauvegardes (>30 jours)
find backups/ -type f -name "*.tar.gz" -mtime +30 -delete
```

## 🔒 SSL/Certificats

```bash
# Renouveler manuellement
sudo certbot renew

# Tester le renouvellement
sudo certbot renew --dry-run

# Copier les certificats après renouvellement
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/
sudo chown legrimoire:legrimoire nginx/ssl/*
docker compose -f docker-compose.prod.yml restart nginx

# Vérifier l'expiration des certificats
sudo certbot certificates
```

## 🗄️ Base de données

```bash
# Se connecter à MongoDB
docker compose -f docker-compose.prod.yml exec mongodb mongosh legrimoire -u legrimoire

# Compter les documents
docker compose -f docker-compose.prod.yml exec mongodb mongosh legrimoire --eval "db.ingredients.countDocuments()"
docker compose -f docker-compose.prod.yml exec mongodb mongosh legrimoire --eval "db.recipes.countDocuments()"

# Importer les ingrédients
docker compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py
```

## 🔧 Maintenance

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Nettoyer Docker
docker system prune -a

# Vérifier l'espace disque
df -h

# Vérifier l'utilisation des volumes Docker
docker system df

# Nettoyer les volumes inutilisés
docker volume prune
```

## 🌐 DNS et réseau

```bash
# Vérifier la résolution DNS
nslookup legrimoireonline.ca
dig legrimoireonline.ca

# Vérifier les ports ouverts
sudo netstat -tulpn | grep -E ':(80|443)'

# Vérifier le pare-feu
sudo ufw status verbose

# Tester la connexion HTTPS
curl -I https://legrimoireonline.ca

# Tester l'API
curl https://legrimoireonline.ca/api/health
```

## 🚨 Dépannage rapide

### Le site ne charge pas

```bash
# 1. Vérifier les conteneurs
docker compose -f docker-compose.prod.yml ps

# 2. Vérifier les logs nginx
docker compose -f docker-compose.prod.yml logs nginx --tail=50

# 3. Redémarrer nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Erreur 502 Bad Gateway

```bash
# 1. Vérifier le backend
docker compose -f docker-compose.prod.yml logs backend --tail=50

# 2. Redémarrer le backend
docker compose -f docker-compose.prod.yml restart backend

# 3. Vérifier la connexion backend
docker compose -f docker-compose.prod.yml exec nginx ping backend
```

### Erreur SSL

```bash
# 1. Vérifier les certificats
ls -la nginx/ssl/

# 2. Recopier les certificats
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/*.pem nginx/ssl/
sudo chown legrimoire:legrimoire nginx/ssl/*

# 3. Redémarrer nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### MongoDB ne démarre pas

```bash
# 1. Vérifier les logs
docker compose -f docker-compose.prod.yml logs mongodb --tail=50

# 2. Vérifier l'espace disque
df -h

# 3. Redémarrer MongoDB
docker compose -f docker-compose.prod.yml restart mongodb
```

### Manque d'espace disque

```bash
# 1. Vérifier l'utilisation
df -h
du -sh /* | sort -h

# 2. Nettoyer Docker
docker system prune -a
docker volume prune

# 3. Nettoyer les anciennes sauvegardes
find backups/ -type f -mtime +30 -delete

# 4. Nettoyer les logs système
sudo journalctl --vacuum-time=7d
```

## 📝 Variables d'environnement importantes

```bash
# Éditer les variables
nano .env.production

# Variables critiques:
# - MONGODB_PASSWORD
# - SECRET_KEY
# - JWT_SECRET_KEY
# - NEXT_PUBLIC_API_URL

# Redémarrer après modification
docker compose -f docker-compose.prod.yml restart
```

## 🔐 Sécurité

```bash
# Vérifier les mises à jour disponibles
sudo apt update
sudo apt list --upgradable

# Vérifier les connexions SSH
sudo grep "Accepted" /var/log/auth.log | tail -20

# Vérifier les utilisateurs connectés
who
w

# Vérifier les processus Docker
docker ps
docker stats
```

## 📞 Liens utiles

- **Site** : https://legrimoireonline.ca
- **API Docs** : https://legrimoireonline.ca/docs
- **Vultr Panel** : https://my.vultr.com/
- **GoDaddy** : https://www.godaddy.com/
- **SSL Test** : https://www.ssllabs.com/ssltest/
- **DNS Test** : https://www.whatsmydns.net/

## 🆘 Support

- Documentation : `/docs/deployment/`
- GitHub Issues : https://github.com/sparck75/le-grimoire/issues
- Vultr Support : https://my.vultr.com/support/

---

**Conseil** : Ajoutez cette page à vos favoris pour un accès rapide aux commandes courantes !
