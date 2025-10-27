# Guide Rapide de Déploiement - Le Grimoire

Ce guide est un résumé rapide pour déployer Le Grimoire sur Vultr avec le domaine legrimoireonline.ca. Pour les détails complets, consultez [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md).

## 🚀 Déploiement en 10 étapes

### 1️⃣ Créer le serveur Vultr (10 min)

1. Allez sur https://my.vultr.com/
2. "Deploy New Server" → Ubuntu 22.04 LTS
3. Plan : 2 vCPU, 4 GB RAM minimum
4. Notez votre **IP** : `XXX.XXX.XXX.XXX`

### 2️⃣ Configurer DNS sur GoDaddy (5 min)

1. https://godaddy.com/ → My Products → legrimoireonline.ca → DNS
2. Supprimer les enregistrements A et CNAME existants
3. Ajouter enregistrement A :
   - Name: `@` → Value: `XXX.XXX.XXX.XXX`
4. Ajouter enregistrement A :
   - Name: `www` → Value: `XXX.XXX.XXX.XXX`

📖 **Guide détaillé** : [GODADDY_DNS.md](./GODADDY_DNS.md)

### 3️⃣ Se connecter au serveur (1 min)

```bash
ssh root@XXX.XXX.XXX.XXX
```

### 4️⃣ Mettre à jour et installer Docker (5 min)

```bash
# Mise à jour
apt update && apt upgrade -y

# Installer Docker (includes Docker Compose plugin)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Vérifier l'installation
docker --version
docker compose version
```

### 5️⃣ Configurer le pare-feu (2 min)

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 6️⃣ Cloner le projet (2 min)

```bash
mkdir -p /root/apps && cd /root/apps
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
```

### 7️⃣ Créer le fichier .env.production (3 min)

```bash
cp .env.production.example .env.production
nano .env.production
```

**Modifiez les valeurs suivantes** :

```bash
# Générer des secrets sécurisés
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

# Mots de passe MongoDB et PostgreSQL
MONGODB_USER=legrimoire
MONGODB_PASSWORD=VotreMotDePasseMongoDB456
POSTGRES_PASSWORD=VotreMotDePassePostgreSQL123

# URLs
NEXT_PUBLIC_API_URL=https://legrimoireonline.ca

# Mettre à jour aussi MONGODB_URL avec le mot de passe MongoDB
# MONGODB_URL=mongodb://legrimoire:VotreMotDePasseMongoDB456@mongodb:27017/legrimoire?authSource=admin
```

### 8️⃣ Configurer Nginx pour le domaine (3 min)

```bash
nano nginx/nginx.conf
```

**Remplacez** `server_name localhost 192.168.1.133 _;` par :
```nginx
server_name legrimoireonline.ca www.legrimoireonline.ca;
```

### 9️⃣ Créer des certificats temporaires (2 min)

```bash
mkdir -p nginx/ssl certbot/www

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=CA/ST=Quebec/L=Montreal/O=LeGrimoire/CN=legrimoireonline.ca"
```

### 🔟 Démarrer l'application (5 min)

```bash
docker compose -f docker-compose.prod.yml up -d --build

# Vérifier
docker compose -f docker-compose.prod.yml ps
```

---

## 🔒 Configuration SSL (15 min)

⏱️ **Attendez que le DNS soit propagé** avant cette étape (vérifiez avec `nslookup legrimoireonline.ca`).

### Obtenir le certificat Let's Encrypt

```bash
# Installer Certbot
apt install -y certbot

# Arrêter nginx temporairement
docker compose -f docker-compose.prod.yml stop nginx

# Obtenir le certificat (remplacez votre-email@example.com)
certbot certonly --standalone \
  -d legrimoireonline.ca -d www.legrimoireonline.ca \
  --email votre-email@example.com \
  --agree-tos --non-interactive

# Copier les certificats
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

# Redémarrer nginx
docker compose -f docker-compose.prod.yml start nginx
```

### Configurer le renouvellement automatique

```bash
cat > /root/renew-ssl.sh << 'EOF'
#!/bin/bash
cd /root/apps/le-grimoire
docker compose -f docker-compose.prod.yml stop nginx
certbot renew --quiet
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/
docker compose -f docker-compose.prod.yml start nginx
echo "$(date): Certificat SSL renouvelé" >> /var/log/ssl-renewal.log
EOF

chmod +x /root/renew-ssl.sh

# Ajouter au cron (tous les lundis à 3h)
(crontab -l 2>/dev/null; echo "0 3 * * 1 /root/renew-ssl.sh") | crontab -
```

---

## ✅ Vérification finale

### Tester le site

1. ✅ http://legrimoireonline.ca → Devrait rediriger vers HTTPS
2. ✅ https://legrimoireonline.ca → Site principal
3. ✅ https://www.legrimoireonline.ca → Devrait fonctionner
4. ✅ https://legrimoireonline.ca/docs → Documentation API
5. ✅ https://legrimoireonline.ca/health → "healthy"

### Vérifier SSL

- https://www.ssllabs.com/ssltest/analyze.html?d=legrimoireonline.ca

### Initialiser la base de données

```bash
cd /root/apps/le-grimoire

# Importer les ingrédients (5942 items)
docker compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py

# Vérifier
docker compose -f docker-compose.prod.yml exec mongodb mongosh -u legrimoire -p VOTRE_MONGO_PASSWORD --authenticationDatabase admin --eval "use legrimoire; db.ingredients.countDocuments()"
```

---

## 📋 Commandes utiles

### Gestion de l'application

```bash
cd /root/apps/le-grimoire

# Logs
docker compose -f docker-compose.prod.yml logs -f

# Redémarrer
docker compose -f docker-compose.prod.yml restart

# Arrêter
docker compose -f docker-compose.prod.yml down

# Mettre à jour
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Monitoring

```bash
# Statut des conteneurs
docker compose -f docker-compose.prod.yml ps

# Ressources
docker stats

# Espace disque
df -h

# Processus
htop
```

### Sauvegardes

```bash
# Créer une sauvegarde manuelle
docker exec le-grimoire-mongodb mongodump --username=legrimoire --password=VOTRE_MONGO_PASSWORD --authenticationDatabase=admin --db=legrimoire --out=/backup
docker cp le-grimoire-mongodb:/backup ./backup-$(date +%Y%m%d)

# Restaurer
docker cp ./backup-20240115 le-grimoire-mongodb:/backup
docker exec le-grimoire-mongodb mongorestore --username=legrimoire --password=VOTRE_MONGO_PASSWORD --authenticationDatabase=admin --db=legrimoire /backup/legrimoire
```

---

## 🐛 Dépannage rapide

### Le site ne charge pas

```bash
# Vérifier les conteneurs
docker compose -f docker-compose.prod.yml ps

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs frontend

# Redémarrer
docker compose -f docker-compose.prod.yml restart
```

### DNS ne fonctionne pas

```bash
# Vérifier la propagation
nslookup legrimoireonline.ca

# Devrait retourner votre IP Vultr
# Si non, attendez ou vérifiez la config GoDaddy
```

### Erreur SSL

```bash
# Vérifier les certificats
ls -l nginx/ssl/
certbot certificates

# Renouveler
/root/renew-ssl.sh
```

### Performance lente

```bash
# Vérifier les ressources
docker stats
htop

# Nettoyer Docker
docker system prune -a

# Si besoin, upgrader le serveur Vultr
```

---

## 📚 Documentation complète

- **Déploiement Vultr détaillé** : [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md)
- **Configuration DNS GoDaddy** : [GODADDY_DNS.md](./GODADDY_DNS.md)
- **Guide de démarrage** : [../getting-started/QUICKSTART.md](../getting-started/QUICKSTART.md)
- **Architecture** : [../architecture/OVERVIEW.md](../architecture/OVERVIEW.md)

---

## 💰 Coûts estimés

| Service | Coût mensuel | Notes |
|---------|--------------|-------|
| Vultr VPS (2 vCPU, 4 GB) | $18-24 | Minimum recommandé |
| Domaine GoDaddy (.ca) | $15-20/an | ≈$1.50/mois |
| Backups Vultr | $1.50 | Optionnel mais recommandé |
| Let's Encrypt SSL | Gratuit | ✅ |
| **Total** | **≈$20-26/mois** | |

Pour production haute performance : $48-72/mois (4 vCPU, 8 GB RAM)

---

## 🎉 C'est fait !

Votre application **Le Grimoire** est maintenant en production sur :

🌍 **https://legrimoireonline.ca**

### Prochaines étapes

1. [ ] Créer un compte admin
2. [ ] Importer vos recettes
3. [ ] Configurer les sauvegardes automatiques
4. [ ] Configurer le monitoring
5. [ ] Ajouter Google Analytics (optionnel)
6. [ ] Configurer l'email (optionnel)

---

## 📞 Support

- 📖 [Documentation](../README.md)
- 🐛 [GitHub Issues](https://github.com/sparck75/le-grimoire/issues)
- 💬 [Discussions](https://github.com/sparck75/le-grimoire/discussions)
