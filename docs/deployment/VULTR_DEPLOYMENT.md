# Guide de déploiement sur Vultr - Le Grimoire

Ce guide vous accompagnera dans le déploiement de Le Grimoire sur un serveur Vultr avec le domaine `legrimoireonline.ca`.

## 📋 Prérequis

- Serveur Vultr avec Ubuntu 22.04 LTS (minimum 2GB RAM, 2 vCPU, 50GB SSD)
- Domaine `legrimoireonline.ca` configuré sur GoDaddy
- Accès SSH au serveur
- Connaissances de base en ligne de commande Linux

### Versions des composants

Le déploiement utilisera les versions suivantes (gérées via Docker) :
- **Ubuntu** : 22.04 LTS
- **Docker Engine** : 24.0+ (dernière version stable)
- **Docker Compose** : v2.20+ (plugin)
- **MongoDB** : 7.0
- **PostgreSQL** : 15 (optionnel, legacy)
- **Redis** : 7
- **Nginx** : Alpine (dernière)
- **Python** : 3.11 (backend)
- **Node.js** : 20 (frontend)

## 🚀 Étape 1 : Configuration initiale du serveur Vultr

### 1.1 Créer un serveur Vultr

1. Connectez-vous à votre compte Vultr : https://my.vultr.com/
2. Cliquez sur **"Deploy New Server"**
3. Choisissez les options suivantes :
   - **Server Type** : Cloud Compute - Shared CPU
   - **Location** : Choisissez le datacenter le plus proche de vos utilisateurs (ex: Toronto pour le Canada)
   - **Image** : Ubuntu 22.04 LTS x64
   - **Plan** : Minimum 2GB RAM ($12/mois) - recommandé 4GB RAM ($24/mois) pour de meilleures performances
   - **Additional Features** : 
     - ✅ Enable IPv6
     - ✅ Enable Auto Backups (recommandé)
   - **Server Hostname** : `legrimoire-prod`
   - **Label** : `Le Grimoire Production`

4. Cliquez sur **"Deploy Now"**
5. Attendez que le serveur soit "Running" (environ 2-3 minutes)
6. Notez l'**adresse IP publique** de votre serveur (exemple: 45.76.123.45)

### 1.2 Première connexion SSH

```bash
# Remplacez YOUR_SERVER_IP par l'IP de votre serveur
ssh root@YOUR_SERVER_IP

# Lors de la première connexion, vous devrez accepter l'empreinte du serveur
# Tapez 'yes' et appuyez sur Enter

# Le mot de passe root est disponible dans le panneau Vultr (section "Settings" -> "View Password")
```

### 1.3 Mise à jour du système

```bash
# Mettre à jour la liste des paquets
apt update

# Mettre à jour les paquets installés
apt upgrade -y

# Installer les dépendances de base
apt install -y curl wget git ufw vim htop net-tools

# Redémarrer si nécessaire
reboot
```

## 🔐 Étape 2 : Configuration de la sécurité

### 2.1 Créer un utilisateur non-root

```bash
# Se connecter en tant que root
ssh root@YOUR_SERVER_IP

# Créer un utilisateur 'legrimoire'
adduser legrimoire

# Vous serez invité à définir un mot de passe - choisissez un mot de passe fort
# Appuyez sur Enter pour laisser les autres champs vides

# Ajouter l'utilisateur au groupe sudo
usermod -aG sudo legrimoire

# Vérifier que l'utilisateur a été créé
id legrimoire
```

### 2.2 Configurer l'accès SSH par clé (recommandé)

Sur **votre ordinateur local** :

```bash
# Générer une paire de clés SSH (si vous n'en avez pas déjà)
ssh-keygen -t ed25519 -C "votre_email@example.com"

# Appuyez sur Enter pour accepter l'emplacement par défaut
# Définissez une phrase de passe (optionnel mais recommandé)

# Copier la clé publique vers le serveur
ssh-copy-id legrimoire@YOUR_SERVER_IP

# Tester la connexion
ssh legrimoire@YOUR_SERVER_IP
```

Si `ssh-copy-id` ne fonctionne pas, faites-le manuellement :

```bash
# Sur votre ordinateur local, afficher votre clé publique
cat ~/.ssh/id_ed25519.pub

# Copier la sortie (commence par ssh-ed25519...)

# Sur le serveur, en tant qu'utilisateur legrimoire
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys

# Coller votre clé publique, sauvegarder (Ctrl+X, Y, Enter)
chmod 600 ~/.ssh/authorized_keys
```

### 2.3 Configurer le pare-feu (UFW)

```bash
# Permettre SSH (IMPORTANT : faites ceci AVANT d'activer le pare-feu)
sudo ufw allow OpenSSH

# Permettre HTTP (port 80)
sudo ufw allow 80/tcp

# Permettre HTTPS (port 443)
sudo ufw allow 443/tcp

# Activer le pare-feu
sudo ufw enable

# Vérifier le statut
sudo ufw status verbose
```

### 2.4 Sécuriser SSH (optionnel mais recommandé)

```bash
# Éditer la configuration SSH
sudo nano /etc/ssh/sshd_config

# Modifier les lignes suivantes (enlever le # au début si nécessaire) :
# PermitRootLogin no
# PasswordAuthentication no  # Seulement si vous avez configuré les clés SSH
# PubkeyAuthentication yes

# Sauvegarder et quitter (Ctrl+X, Y, Enter)

# Redémarrer le service SSH
sudo systemctl restart sshd
```

⚠️ **ATTENTION** : Ne désactivez `PasswordAuthentication` que si vous avez testé avec succès la connexion par clé SSH !

## 🐳 Étape 3 : Installation de Docker

```bash
# Se connecter en tant qu'utilisateur legrimoire
ssh legrimoire@YOUR_SERVER_IP

# Installer les dépendances
sudo apt install -y ca-certificates curl gnupg lsb-release

# Ajouter la clé GPG officielle de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Mettre à jour la liste des paquets
sudo apt update

# Installer Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker legrimoire

# Déconnexion et reconnexion pour appliquer les changements de groupe
exit
ssh legrimoire@YOUR_SERVER_IP

# Vérifier l'installation
docker --version
docker compose version
```

## 📦 Étape 4 : Cloner et configurer Le Grimoire

### 4.1 Cloner le dépôt

```bash
# Créer un répertoire pour les applications
mkdir -p ~/apps
cd ~/apps

# Cloner le dépôt
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
```

### 4.2 Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.production.example .env.production

# Éditer le fichier
nano .env.production
```

Configurez les variables suivantes (voir le fichier `.env.production.example` pour plus de détails) :

```bash
# Database Configuration (MongoDB)
MONGODB_USER=legrimoire
MONGODB_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE
MONGODB_URL=mongodb://legrimoire:CHANGEZ_CE_MOT_DE_PASSE@mongodb:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire

# PostgreSQL (Legacy - optionnel)
POSTGRES_USER=grimoire
POSTGRES_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE
POSTGRES_DB=le_grimoire

# Application Secrets - IMPORTANT: Changez ces valeurs!
SECRET_KEY=GÉNÉREZ_UNE_CLÉ_ALÉATOIRE_DE_32_CARACTÈRES
JWT_SECRET_KEY=GÉNÉREZ_UNE_AUTRE_CLÉ_ALÉATOIRE_DE_32_CARACTÈRES

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://legrimoireonline.ca

# OAuth Configuration (optionnel)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_CLIENT_SECRET=

# Email Configuration (pour les notifications - optionnel)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@legrimoireonline.ca
```

### 4.3 Générer des clés secrètes sécurisées

```bash
# Générer une clé aléatoire pour SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Générer une autre clé pour JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copier ces valeurs dans votre fichier .env.production
```

### 4.4 Créer les répertoires nécessaires

```bash
# Créer les répertoires pour les certificats SSL et les données
mkdir -p nginx/ssl
mkdir -p data/mongodb
mkdir -p backups
```

## 🔒 Étape 5 : Configuration SSL avec Let's Encrypt

### 5.1 Installer Certbot

```bash
# Installer Certbot
sudo apt install -y certbot

# Vérifier l'installation
certbot --version
```

### 5.2 Obtenir les certificats SSL

⚠️ **IMPORTANT** : Avant d'exécuter cette commande, assurez-vous que votre domaine pointe vers l'IP de votre serveur (voir la section GoDaddy ci-dessous).

```bash
# Arrêter temporairement les services Docker s'ils tournent
cd ~/apps/le-grimoire
docker compose -f docker-compose.prod.yml down

# Obtenir le certificat
sudo certbot certonly --standalone -d legrimoireonline.ca -d www.legrimoireonline.ca

# Suivez les instructions :
# - Entrez votre adresse email
# - Acceptez les conditions d'utilisation
# - Décidez si vous voulez partager votre email avec l'EFF

# Les certificats seront créés dans :
# /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem
# /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem
```

### 5.3 Copier les certificats dans le répertoire nginx

```bash
# Copier les certificats
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem ~/apps/le-grimoire/nginx/ssl/
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem ~/apps/le-grimoire/nginx/ssl/

# Changer les permissions
sudo chown legrimoire:legrimoire ~/apps/le-grimoire/nginx/ssl/*
chmod 644 ~/apps/le-grimoire/nginx/ssl/fullchain.pem
chmod 600 ~/apps/le-grimoire/nginx/ssl/privkey.pem
```

### 5.4 Configurer le renouvellement automatique

```bash
# Tester le renouvellement (mode dry-run)
sudo certbot renew --dry-run

# Créer un script de renouvellement qui copie les certificats
sudo nano /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh
```

Contenu du script :

```bash
#!/bin/bash
cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem /home/legrimoire/apps/le-grimoire/nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem /home/legrimoire/apps/le-grimoire/nginx/ssl/
chown legrimoire:legrimoire /home/legrimoire/apps/le-grimoire/nginx/ssl/*
cd /home/legrimoire/apps/le-grimoire && docker compose -f docker-compose.prod.yml restart nginx
```

```bash
# Rendre le script exécutable
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh

# Le renouvellement automatique est géré par un timer systemd
sudo systemctl status certbot.timer
```

## 🚢 Étape 6 : Déployer l'application

### 6.1 Construire et démarrer les conteneurs

```bash
cd ~/apps/le-grimoire

# Construire les images
docker compose -f docker-compose.prod.yml build

# Démarrer les services en arrière-plan
docker compose -f docker-compose.prod.yml up -d

# Vérifier que tous les conteneurs sont démarrés
docker compose -f docker-compose.prod.yml ps

# Voir les logs
docker compose -f docker-compose.prod.yml logs -f
```

### 6.2 Initialiser la base de données MongoDB

```bash
# Attendre que MongoDB soit prêt (environ 30 secondes)
sleep 30

# Vérifier que MongoDB est accessible
docker compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.adminCommand('ping')"

# Importer les ingrédients OpenFoodFacts (si nécessaire)
docker compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py

# Vérifier que les ingrédients sont importés
docker compose -f docker-compose.prod.yml exec mongodb mongosh legrimoire --eval "db.ingredients.countDocuments()"
# Devrait retourner environ 5942
```

### 6.3 Vérifier le déploiement

```bash
# Vérifier les logs de tous les services
docker compose -f docker-compose.prod.yml logs

# Vérifier les logs d'un service spécifique
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs nginx

# Tester l'accès local
curl http://localhost
curl http://localhost/api/health
```

### 6.4 Tester depuis votre navigateur

1. Ouvrez https://legrimoireonline.ca
2. Vérifiez que le site charge correctement
3. Testez la recherche d'ingrédients
4. Testez la création d'une recette

## 🔄 Étape 7 : Configuration de la sauvegarde automatique

### 7.1 Sauvegarde avec deploy.sh (Recommandé)

La méthode la plus simple est d'utiliser le script deploy.sh existant :

```bash
# Sauvegarde manuelle
cd ~/apps/le-grimoire
./deploy.sh backup
```

### 7.2 Créer un script de sauvegarde dédié (Optionnel)

Si vous préférez avoir un script de sauvegarde séparé, créez `backup.sh` :

```bash
# Créer le script
nano ~/apps/le-grimoire/backup.sh
```

Contenu du script :

```bash
#!/bin/bash
BACKUP_DIR="/home/legrimoire/apps/le-grimoire/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGODB_CONTAINER="le-grimoire-mongodb-prod"

echo "Starting backup at $(date)"

# Créer le répertoire de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Sauvegarder MongoDB
docker exec $MONGODB_CONTAINER mongodump \
  --out /tmp/backup_$DATE \
  --authenticationDatabase admin \
  -u legrimoire \
  -p "$MONGODB_PASSWORD"

# Copier le backup depuis le conteneur
docker cp $MONGODB_CONTAINER:/tmp/backup_$DATE "$BACKUP_DIR/mongodb_backup_$DATE"

# Nettoyer les anciens backups (garder les 7 derniers jours)
find "$BACKUP_DIR" -type d -name "mongodb_backup_*" -mtime +7 -exec rm -rf {} \;

# Compresser le backup
cd "$BACKUP_DIR"
tar -czf "mongodb_backup_$DATE.tar.gz" "mongodb_backup_$DATE"
rm -rf "mongodb_backup_$DATE"

echo "Backup completed at $(date)"
echo "Backup saved to: $BACKUP_DIR/mongodb_backup_$DATE.tar.gz"
```

```bash
# Rendre le script exécutable
chmod +x ~/apps/le-grimoire/backup.sh

# Tester le script
~/apps/le-grimoire/backup.sh
```

### 7.3 Configurer une tâche cron pour les sauvegardes automatiques

```bash
# Éditer le crontab
crontab -e

# Option 1: Utiliser deploy.sh (recommandé)
0 3 * * * cd /home/legrimoire/apps/le-grimoire && ./deploy.sh backup >> /home/legrimoire/apps/le-grimoire/backups/backup.log 2>&1

# Option 2: Utiliser backup.sh (si créé)
# 0 3 * * * /home/legrimoire/apps/le-grimoire/backup.sh >> /home/legrimoire/apps/le-grimoire/backups/backup.log 2>&1
```

## 📊 Étape 8 : Monitoring et maintenance

### 8.1 Surveiller les logs

```bash
# Logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# Afficher les dernières 100 lignes
docker compose -f docker-compose.prod.yml logs --tail=100
```

### 8.2 Surveiller l'utilisation des ressources

```bash
# Voir l'utilisation CPU/Mémoire des conteneurs
docker stats

# Voir l'espace disque
df -h

# Voir l'utilisation de la RAM
free -h

# Voir les processus
htop
```

### 8.3 Redémarrer les services

```bash
cd ~/apps/le-grimoire

# Redémarrer tous les services
docker compose -f docker-compose.prod.yml restart

# Redémarrer un service spécifique
docker compose -f docker-compose.prod.yml restart nginx
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart frontend
```

### 8.4 Mettre à jour l'application

```bash
cd ~/apps/le-grimoire

# Sauvegarder les données avant la mise à jour
./deploy.sh backup

# Récupérer les dernières modifications
git pull origin main

# Reconstruire les images
docker compose -f docker-compose.prod.yml build

# Redémarrer avec les nouvelles images
docker compose -f docker-compose.prod.yml up -d

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs -f
```

## 🆘 Dépannage

### Le site n'est pas accessible

```bash
# Vérifier que tous les conteneurs sont en cours d'exécution
docker compose -f docker-compose.prod.yml ps

# Vérifier les logs de nginx
docker compose -f docker-compose.prod.yml logs nginx

# Vérifier que les ports sont ouverts
sudo netstat -tulpn | grep -E ':(80|443)'

# Vérifier le pare-feu
sudo ufw status
```

### Erreur SSL/TLS

```bash
# Vérifier que les certificats existent
ls -la ~/apps/le-grimoire/nginx/ssl/

# Recopier les certificats si nécessaire
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem ~/apps/le-grimoire/nginx/ssl/
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem ~/apps/le-grimoire/nginx/ssl/
sudo chown legrimoire:legrimoire ~/apps/le-grimoire/nginx/ssl/*

# Redémarrer nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Le backend ne démarre pas

```bash
# Vérifier les logs du backend
docker compose -f docker-compose.prod.yml logs backend

# Vérifier que MongoDB est accessible
docker compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.adminCommand('ping')"

# Redémarrer le backend
docker compose -f docker-compose.prod.yml restart backend
```

### Manque d'espace disque

```bash
# Vérifier l'espace disque
df -h

# Nettoyer les anciennes images Docker
docker system prune -a

# Nettoyer les anciens backups
find ~/apps/le-grimoire/backups -type f -name "*.tar.gz" -mtime +30 -delete
```

## 📚 Ressources supplémentaires

- [Configuration GoDaddy DNS](./GODADDY_DNS.md)
- [Guide de sécurité](./SECURITY.md)
- [Configuration avancée Nginx](./NGINX_ADVANCED.md)
- [Documentation officielle Docker](https://docs.docker.com/)
- [Documentation Let's Encrypt](https://letsencrypt.org/docs/)

## ✅ Checklist de déploiement

- [ ] Serveur Vultr créé et accessible via SSH
- [ ] Utilisateur non-root créé
- [ ] Pare-feu UFW configuré
- [ ] Docker et Docker Compose installés
- [ ] Dépôt cloné
- [ ] Variables d'environnement configurées
- [ ] DNS GoDaddy configuré (voir GODADDY_DNS.md)
- [ ] Certificats SSL obtenus
- [ ] Application déployée et accessible
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring mis en place
- [ ] Documentation lue et comprise

## 🎉 Félicitations !

Votre application Le Grimoire est maintenant déployée et accessible sur https://legrimoireonline.ca !

Pour toute question ou problème, consultez la documentation ou ouvrez une issue sur GitHub.
