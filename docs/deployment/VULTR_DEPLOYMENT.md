# Guide de Déploiement sur Vultr - Le Grimoire

Ce guide vous accompagne étape par étape pour déployer Le Grimoire sur un serveur Vultr avec le domaine **legrimoireonline.ca**.

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Configuration du serveur Vultr](#configuration-du-serveur-vultr)
3. [Installation des dépendances](#installation-des-dépendances)
4. [Configuration DNS (GoDaddy)](#configuration-dns-godaddy)
5. [Déploiement de l'application](#déploiement-de-lapplication)
6. [Configuration SSL avec Let's Encrypt](#configuration-ssl-avec-lets-encrypt)
7. [Configuration finale](#configuration-finale)
8. [Maintenance](#maintenance)
9. [Dépannage](#dépannage)

---

## Prérequis

### Services requis
- ✅ Compte Vultr actif
- ✅ Domaine **legrimoireonline.ca** enregistré chez GoDaddy
- ✅ Accès SSH à votre serveur
- ✅ Client Git installé localement

### Connaissances recommandées
- Base de Linux (Ubuntu)
- Docker et Docker Compose
- Nginx
- Gestion DNS

---

## Configuration du serveur Vultr

### 1. Créer une instance Vultr

1. **Connectez-vous** à votre compte Vultr : https://my.vultr.com/
2. **Cliquez sur** "Deploy New Server" (ou "+")
3. **Sélectionnez** les options suivantes :

**Type de serveur :**
- Choose Server: **Cloud Compute**

**Localisation :**
- Toronto, Canada (pour un serveur proche du Canada)
- Ou New York/Atlanta pour des performances optimales en Amérique du Nord

**Image du serveur :**
- Operating System: **Ubuntu 22.04 LTS x64**

**Plan du serveur :**
- **Minimum recommandé** : 2 vCPU, 4 GB RAM, 80 GB SSD ($18/mois)
- **Recommandé** : 2 vCPU, 4 GB RAM, 100 GB SSD ($24/mois)
- **Production haute performance** : 4 vCPU, 8 GB RAM, 160 GB SSD ($48/mois)

**Paramètres supplémentaires :**
- ✅ Enable IPv6
- ✅ Enable Auto Backups (recommandé - $1.50/mois)
- ❌ Enable DDOS Protection (optionnel)

**Configuration SSH :**
- **Option 1** : Ajoutez votre clé SSH publique (recommandé)
- **Option 2** : Utilisez un mot de passe root (sera envoyé par email)

**Nom du serveur :**
- Server Hostname: `legrimoire-prod`
- Server Label: `Le Grimoire Production`

4. **Cliquez sur** "Deploy Now"

### 2. Notez les informations du serveur

Une fois le serveur déployé (2-5 minutes), notez :
- **Adresse IP** : `XXX.XXX.XXX.XXX` (ex: 45.76.123.45)
- **Mot de passe root** : (si vous n'utilisez pas de clé SSH)
- **IPv6** : (optionnel)

### 3. Connexion initiale SSH

```bash
# Remplacez XXX.XXX.XXX.XXX par votre IP Vultr
ssh root@XXX.XXX.XXX.XXX
```

Si vous utilisez une clé SSH :
```bash
ssh -i ~/.ssh/votre_cle root@XXX.XXX.XXX.XXX
```

---

## Installation des dépendances

### 1. Mettre à jour le système

```bash
# Mise à jour des paquets
apt update && apt upgrade -y

# Installer les outils de base
apt install -y curl wget git vim ufw htop
```

### 2. Configurer le pare-feu (UFW)

```bash
# Autoriser SSH
ufw allow OpenSSH

# Autoriser HTTP et HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Activer le pare-feu
ufw enable

# Vérifier le statut
ufw status
```

Vous devriez voir :
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 3. Installer Docker

```bash
# Installer les prérequis
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Ajouter la clé GPG officielle de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le dépôt Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Vérifier l'installation
docker --version
```

### 4. Installer Docker Compose

```bash
# Télécharger Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Rendre exécutable
chmod +x /usr/local/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

### 5. Créer un utilisateur non-root (recommandé)

```bash
# Créer l'utilisateur
adduser legrimoire

# Ajouter aux groupes sudo et docker
usermod -aG sudo legrimoire
usermod -aG docker legrimoire

# Tester la connexion
su - legrimoire
docker ps  # Devrait fonctionner sans sudo
exit
```

---

## Configuration DNS (GoDaddy)

### 1. Connexion à GoDaddy

1. Allez sur https://godaddy.com/
2. Connectez-vous avec votre compte
3. Cliquez sur votre nom en haut à droite → **My Products**
4. Trouvez **legrimoireonline.ca** et cliquez sur **DNS**

### 2. Configuration des enregistrements DNS

#### A. Supprimer les enregistrements par défaut

Dans la section **DNS Management**, supprimez :
- Tous les enregistrements A existants
- L'enregistrement CNAME avec le nom "@" (s'il existe)

#### B. Ajouter les nouveaux enregistrements

**Enregistrement A principal (domaine racine)** :
- **Type** : A
- **Name** : @ (représente legrimoireonline.ca)
- **Value** : `XXX.XXX.XXX.XXX` (votre IP Vultr)
- **TTL** : 600 seconds (ou 1 hour)

Cliquez sur **Save** ou **Add Record**.

**Enregistrement A pour www** :
- **Type** : A
- **Name** : www
- **Value** : `XXX.XXX.XXX.XXX` (même IP Vultr)
- **TTL** : 600 seconds

Cliquez sur **Save** ou **Add Record**.

**Alternative : Utiliser un CNAME pour www (optionnel)** :
- **Type** : CNAME
- **Name** : www
- **Value** : legrimoireonline.ca
- **TTL** : 1 hour

#### C. Configuration finale

Vos enregistrements DNS devraient ressembler à :

```
Type    Name    Value               TTL
----    ----    -----               ---
A       @       XXX.XXX.XXX.XXX     600
A       www     XXX.XXX.XXX.XXX     600
```

Ou avec CNAME :
```
Type    Name    Value                   TTL
----    ----    -----                   ---
A       @       XXX.XXX.XXX.XXX         600
CNAME   www     legrimoireonline.ca     3600
```

### 3. Temps de propagation DNS

⏱️ **IMPORTANT** : La propagation DNS peut prendre de **15 minutes à 48 heures**.

#### Vérifier la propagation

```bash
# Depuis votre ordinateur local
nslookup legrimoireonline.ca

# Ou
dig legrimoireonline.ca

# Ou en ligne
# https://dnschecker.org/#A/legrimoireonline.ca
```

Vous devriez voir votre IP Vultr dans les résultats.

---

## Déploiement de l'application

### 1. Cloner le dépôt

```bash
# Se connecter au serveur (en tant que legrimoire ou root)
ssh legrimoire@XXX.XXX.XXX.XXX

# Créer le répertoire de l'application
mkdir -p /home/legrimoire/apps
cd /home/legrimoire/apps

# Cloner le dépôt
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
```

### 2. Créer le fichier .env de production

```bash
# Copier le template
cp .env.example .env

# Éditer le fichier
nano .env
```

**Contenu du fichier `.env`** :

```bash
# ==========================================
# PRODUCTION ENVIRONMENT - legrimoireonline.ca
# ==========================================

# Database Configuration (PostgreSQL)
POSTGRES_USER=legrimoire_prod
POSTGRES_PASSWORD=CHANGEZ_MOI_MOT_DE_PASSE_TRES_SECURISE_123
POSTGRES_DB=le_grimoire

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=legrimoire
MONGO_INITDB_ROOT_PASSWORD=CHANGEZ_MOI_MONGODB_PASSWORD_456
MONGODB_URL=mongodb://legrimoire:CHANGEZ_MOI_MONGODB_PASSWORD_456@mongodb:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire

# Application Secrets (GÉNÉRER DES CLÉS UNIQUES!)
SECRET_KEY=GENERATE_A_RANDOM_SECRET_KEY_HERE_789
JWT_SECRET_KEY=GENERATE_A_RANDOM_JWT_SECRET_KEY_HERE_012

# OAuth Configuration (Optionnel - si vous utilisez Google/Apple login)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_CLIENT_SECRET=

# Redis Configuration
REDIS_URL=redis://redis:6379

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://legrimoireonline.ca
BACKEND_URL=http://backend:8000

# OCR Service
OCR_ENGINE=tesseract

# Grocery Store Scraper
SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; LeGrimoire/1.0)
SCRAPER_RATE_LIMIT_SECONDS=2
```

**🔐 IMPORTANT - Générer des secrets sécurisés** :

```bash
# Générer SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Générer JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Ou utiliser OpenSSL
openssl rand -base64 64
```

Copiez les valeurs générées dans votre `.env`.

### 3. Modifier la configuration Nginx pour le domaine

```bash
nano nginx/nginx.conf
```

**Remplacez le contenu par** :

```nginx
events {
    worker_connections 1024;
}

http {
    # Configuration de base
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    
    # Upstreams
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # Redirection HTTP vers HTTPS
    server {
        listen 80;
        listen [::]:80;
        server_name legrimoireonline.ca www.legrimoireonline.ca;
        
        # ACME Challenge pour Let's Encrypt
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Rediriger tout vers HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # Configuration HTTPS
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name legrimoireonline.ca www.legrimoireonline.ca;

        # Certificats SSL (seront configurés par Let's Encrypt)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # Configuration SSL moderne
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Frontend - Next.js
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # CORS headers
            add_header Access-Control-Allow-Origin https://legrimoireonline.ca always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            add_header Access-Control-Allow-Credentials "true" always;
            
            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # API Documentation
        location /docs {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 4. Créer le répertoire pour Let's Encrypt

```bash
# Créer les répertoires nécessaires
mkdir -p nginx/ssl
mkdir -p certbot/www

# Créer des certificats temporaires auto-signés pour le premier démarrage
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=CA/ST=Quebec/L=Montreal/O=LeGrimoire/CN=legrimoireonline.ca"
```

### 5. Modifier docker-compose.prod.yml

```bash
nano docker-compose.prod.yml
```

Assurez-vous que la section nginx contient :

```yaml
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: le-grimoire-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - frontend
      - backend
    networks:
      - grimoire-network
```

### 6. Démarrer l'application

```bash
# Construire et démarrer les conteneurs
docker-compose -f docker-compose.prod.yml up -d --build

# Vérifier que tout fonctionne
docker-compose -f docker-compose.prod.yml ps

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. Vérifier l'accès HTTP (avant SSL)

Ouvrez votre navigateur et testez :
- http://legrimoireonline.ca (devrait afficher votre site)
- http://XXX.XXX.XXX.XXX (votre IP - devrait aussi fonctionner)

⚠️ **Note** : À ce stade, HTTPS ne fonctionnera pas encore car nous utilisons un certificat auto-signé.

---

## Configuration SSL avec Let's Encrypt

### 1. Installer Certbot

```bash
# Installer Certbot
apt install -y certbot python3-certbot-nginx

# Ou via snap (recommandé)
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
```

### 2. Obtenir un certificat SSL

**Méthode 1 : Certbot standalone (RECOMMANDÉ pour la première fois)**

```bash
# Arrêter nginx temporairement
docker-compose -f docker-compose.prod.yml stop nginx

# Obtenir le certificat
certbot certonly --standalone -d legrimoireonline.ca -d www.legrimoireonline.ca --email votre-email@example.com --agree-tos --non-interactive

# Les certificats seront dans /etc/letsencrypt/live/legrimoireonline.ca/

# Copier les certificats dans le répertoire nginx
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

# Redémarrer nginx
docker-compose -f docker-compose.prod.yml start nginx
```

**Méthode 2 : Avec nginx actif (webroot)**

```bash
# Nginx doit être en cours d'exécution
certbot certonly --webroot -w /home/legrimoire/apps/le-grimoire/certbot/www -d legrimoireonline.ca -d www.legrimoireonline.ca --email votre-email@example.com --agree-tos --non-interactive

# Copier les certificats
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

# Recharger nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 3. Configurer le renouvellement automatique

Les certificats Let's Encrypt expirent après 90 jours. Configurez le renouvellement automatique :

```bash
# Créer un script de renouvellement
cat > /root/renew-ssl.sh << 'EOF'
#!/bin/bash
# Script de renouvellement SSL pour Le Grimoire

# Arrêter nginx
cd /home/legrimoire/apps/le-grimoire
docker-compose -f docker-compose.prod.yml stop nginx

# Renouveler le certificat
certbot renew --quiet

# Copier les nouveaux certificats
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

# Redémarrer nginx
docker-compose -f docker-compose.prod.yml start nginx

# Log
echo "$(date): Certificat SSL renouvelé" >> /var/log/ssl-renewal.log
EOF

# Rendre exécutable
chmod +x /root/renew-ssl.sh

# Ajouter au cron (s'exécute tous les lundis à 3h du matin)
(crontab -l 2>/dev/null; echo "0 3 * * 1 /root/renew-ssl.sh") | crontab -

# Ou avec systemd timer (plus moderne)
# Tester le renouvellement
certbot renew --dry-run
```

### 4. Vérifier HTTPS

Ouvrez votre navigateur :
- https://legrimoireonline.ca ✅ (devrait fonctionner avec certificat valide)
- http://legrimoireonline.ca → devrait rediriger vers HTTPS
- https://www.legrimoireonline.ca ✅

Testez votre SSL :
- https://www.ssllabs.com/ssltest/analyze.html?d=legrimoireonline.ca

---

## Configuration finale

### 1. Initialiser la base de données MongoDB

```bash
cd /home/legrimoire/apps/le-grimoire

# Importer les ingrédients OpenFoodFacts
docker-compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py

# Vérifier le nombre d'ingrédients (devrait être 5942)
docker-compose -f docker-compose.prod.yml exec mongodb mongosh -u legrimoire -p VOTRE_MONGO_PASSWORD --authenticationDatabase admin --eval "use legrimoire; db.ingredients.countDocuments()"
```

### 2. Créer un utilisateur admin (optionnel)

Si votre application a un système d'authentification :

```bash
# Accéder au backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Créer un utilisateur via Python
python -c "from app.models.mongodb import User; import asyncio; asyncio.run(User.create_admin('admin@legrimoireonline.ca', 'PASSWORD'))"
```

### 3. Configurer les sauvegardes automatiques

```bash
# Créer un script de sauvegarde
cat > /root/backup-grimoire.sh << 'EOF'
#!/bin/bash
# Script de sauvegarde pour Le Grimoire

BACKUP_DIR="/home/legrimoire/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/legrimoire/apps/le-grimoire"

mkdir -p $BACKUP_DIR

# Sauvegarder MongoDB
docker exec le-grimoire-mongodb mongodump --username=legrimoire --password=VOTRE_MONGO_PASSWORD --authenticationDatabase=admin --db=legrimoire --out=/backup
docker cp le-grimoire-mongodb:/backup $BACKUP_DIR/mongodb_$DATE

# Sauvegarder PostgreSQL (si utilisé)
docker exec le-grimoire-db-prod pg_dump -U legrimoire_prod le_grimoire > $BACKUP_DIR/postgres_$DATE.sql

# Sauvegarder les uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/backend/uploads

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -type f -mtime +7 -delete
find $BACKUP_DIR -type d -mtime +7 -delete

echo "$(date): Sauvegarde effectuée" >> /var/log/grimoire-backup.log
EOF

chmod +x /root/backup-grimoire.sh

# Planifier les sauvegardes quotidiennes à 2h du matin
(crontab -l 2>/dev/null; echo "0 2 * * * /root/backup-grimoire.sh") | crontab -
```

### 4. Configurer le monitoring (optionnel mais recommandé)

```bash
# Créer un script de monitoring
cat > /root/check-grimoire.sh << 'EOF'
#!/bin/bash
# Vérifier que tous les services sont actifs

cd /home/legrimoire/apps/le-grimoire

# Vérifier les conteneurs
if [ $(docker-compose -f docker-compose.prod.yml ps -q | wc -l) -lt 5 ]; then
    echo "$(date): ALERTE - Certains conteneurs sont arrêtés" >> /var/log/grimoire-monitor.log
    docker-compose -f docker-compose.prod.yml up -d
fi

# Vérifier l'accès HTTPS
if ! curl -f -s https://legrimoireonline.ca/health > /dev/null; then
    echo "$(date): ALERTE - Site inaccessible" >> /var/log/grimoire-monitor.log
fi
EOF

chmod +x /root/check-grimoire.sh

# Vérifier toutes les 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /root/check-grimoire.sh") | crontab -
```

---

## Maintenance

### Commandes utiles

```bash
# Aller dans le répertoire de l'application
cd /home/legrimoire/apps/le-grimoire

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend

# Redémarrer un service
docker-compose -f docker-compose.prod.yml restart frontend
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx

# Mettre à jour l'application
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Voir l'utilisation des ressources
docker stats

# Nettoyer Docker
docker system prune -a
```

### Mise à jour de l'application

```bash
cd /home/legrimoire/apps/le-grimoire

# Sauvegarder d'abord
/root/backup-grimoire.sh

# Tirer les dernières modifications
git pull origin main

# Reconstruire et redémarrer
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Vérifier
docker-compose -f docker-compose.prod.yml ps
```

---

## Dépannage

### Le site ne charge pas

1. **Vérifier que les conteneurs sont actifs** :
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **Vérifier les logs** :
   ```bash
   docker-compose -f docker-compose.prod.yml logs nginx
   docker-compose -f docker-compose.prod.yml logs frontend
   ```

3. **Vérifier la configuration DNS** :
   ```bash
   nslookup legrimoireonline.ca
   ```

4. **Vérifier le pare-feu** :
   ```bash
   ufw status
   ```

### Erreur de certificat SSL

1. **Vérifier les certificats** :
   ```bash
   ls -l nginx/ssl/
   certbot certificates
   ```

2. **Renouveler manuellement** :
   ```bash
   /root/renew-ssl.sh
   ```

3. **Vérifier la configuration nginx** :
   ```bash
   docker-compose -f docker-compose.prod.yml exec nginx nginx -t
   ```

### MongoDB ne démarre pas

1. **Vérifier les logs** :
   ```bash
   docker-compose -f docker-compose.prod.yml logs mongodb
   ```

2. **Vérifier l'espace disque** :
   ```bash
   df -h
   ```

3. **Redémarrer MongoDB** :
   ```bash
   docker-compose -f docker-compose.prod.yml restart mongodb
   ```

### Performance lente

1. **Vérifier les ressources** :
   ```bash
   htop
   docker stats
   ```

2. **Vérifier l'espace disque** :
   ```bash
   df -h
   ```

3. **Nettoyer Docker** :
   ```bash
   docker system prune -a
   ```

4. **Upgrader le serveur Vultr** vers un plan plus puissant.

---

## 🎉 Félicitations !

Votre application **Le Grimoire** est maintenant déployée sur :
- 🌍 https://legrimoireonline.ca
- 🔒 SSL/TLS activé avec Let's Encrypt
- 🔄 Renouvellement automatique des certificats
- 💾 Sauvegardes automatiques quotidiennes
- 📊 Monitoring automatique

## 📞 Support

En cas de problème :
1. Consultez les logs : `docker-compose -f docker-compose.prod.yml logs`
2. Vérifiez la [documentation complète](../README.md)
3. Ouvrez une [issue sur GitHub](https://github.com/sparck75/le-grimoire/issues)

## 📚 Ressources supplémentaires

- [Vultr Documentation](https://www.vultr.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
