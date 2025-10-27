# Guide de déploiement - Le Grimoire

Documentation complète pour déployer Le Grimoire sur un serveur de production avec le domaine `legrimoireonline.ca`.

## 📚 Documentation disponible

Ce dossier contient toute la documentation nécessaire pour déployer et maintenir Le Grimoire en production :

### 🚀 Guides principaux

1. **[VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md)** - Guide complet de déploiement sur Vultr
   - Configuration du serveur Vultr
   - Installation de Docker
   - Configuration SSL avec Let's Encrypt
   - Déploiement de l'application
   - Sauvegardes automatiques
   - Monitoring et maintenance

2. **[GODADDY_DNS.md](./GODADDY_DNS.md)** - Configuration DNS sur GoDaddy
   - Configuration des enregistrements A
   - Propagation DNS
   - Tests et vérifications
   - Résolution des problèmes courants

3. **[SECURITY.md](./SECURITY.md)** - Guide de sécurité
   - Configuration sécurisée du serveur
   - Gestion des secrets
   - Configuration SSL/TLS
   - Sauvegardes et restauration
   - Réponse aux incidents

## 🎯 Démarrage rapide

### Prérequis
- Serveur Vultr avec Ubuntu 22.04 LTS (minimum 2GB RAM)
- Domaine `legrimoireonline.ca` sur GoDaddy
- Accès SSH au serveur

### Étapes principales

```bash
# 1. Configurer le DNS sur GoDaddy (voir GODADDY_DNS.md)
# Pointer legrimoireonline.ca et www.legrimoireonline.ca vers l'IP du serveur

# 2. Se connecter au serveur Vultr
ssh root@YOUR_SERVER_IP

# 3. Créer un utilisateur et configurer la sécurité (voir VULTR_DEPLOYMENT.md)
adduser legrimoire
usermod -aG sudo legrimoire

# 4. Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker legrimoire

# 5. Cloner le dépôt
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire

# 6. Configurer l'environnement
cp .env.production.example .env.production
nano .env.production  # Éditer avec vos valeurs

# 7. Obtenir les certificats SSL
sudo certbot certonly --standalone -d legrimoireonline.ca -d www.legrimoireonline.ca
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

# 8. Déployer l'application
./deploy.sh deploy
```

## 📦 Fichiers de configuration

### Fichiers principaux

- **`.env.production.example`** - Template pour les variables d'environnement
- **`docker-compose.prod.yml`** - Configuration Docker pour la production
- **`nginx/nginx.prod.conf`** - Configuration Nginx avec SSL
- **`deploy.sh`** - Script de déploiement automatisé

### Structure des fichiers

```
le-grimoire/
├── .env.production.example     # Template de configuration
├── .env.production            # Configuration réelle (à créer, pas dans Git)
├── docker-compose.prod.yml    # Docker Compose production
├── deploy.sh                  # Script de déploiement
├── backup.sh                  # Script de sauvegarde (à créer)
├── nginx/
│   ├── nginx.prod.conf       # Config Nginx production
│   └── ssl/                  # Certificats SSL (à créer)
│       ├── fullchain.pem
│       └── privkey.pem
└── docs/deployment/
    ├── README.md             # Ce fichier
    ├── VULTR_DEPLOYMENT.md   # Guide Vultr complet
    ├── GODADDY_DNS.md        # Guide DNS GoDaddy
    └── SECURITY.md           # Guide de sécurité
```

## 🔧 Utilisation du script de déploiement

Le script `deploy.sh` facilite les opérations de déploiement courantes.

### Mode interactif

```bash
./deploy.sh
```

Un menu s'affichera avec les options suivantes :
1. Deploy (première installation)
2. Update (mise à jour)
3. Start services
4. Stop services
5. Restart services
6. Show logs
7. Show status
8. Backup MongoDB
9. Import ingredients

### Mode commande

```bash
# Déploiement initial
./deploy.sh deploy

# Mise à jour
./deploy.sh update

# Démarrer les services
./deploy.sh start

# Arrêter les services
./deploy.sh stop

# Redémarrer les services
./deploy.sh restart

# Voir les logs
./deploy.sh logs

# Voir le statut
./deploy.sh status

# Créer une sauvegarde
./deploy.sh backup

# Importer les ingrédients
./deploy.sh import-ingredients
```

## 🔐 Configuration des variables d'environnement

Créez votre fichier `.env.production` à partir du template :

```bash
cp .env.production.example .env.production
nano .env.production
```

### Variables importantes à configurer

```bash
# Base de données MongoDB
MONGODB_URL=mongodb://legrimoire:CHANGEZ_MOT_DE_PASSE@mongodb:27017/legrimoire?authSource=admin
MONGODB_PASSWORD=CHANGEZ_MOT_DE_PASSE

# Secrets de l'application (générer avec Python)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# URL de production
NEXT_PUBLIC_API_URL=https://legrimoireonline.ca
```

## 🌐 Configuration DNS

### Sur GoDaddy

1. Se connecter à GoDaddy
2. Aller dans "My Products" > "DNS"
3. Ajouter les enregistrements A :
   - **Type**: A, **Name**: @, **Value**: IP_DU_SERVEUR
   - **Type**: A, **Name**: www, **Value**: IP_DU_SERVEUR

Voir [GODADDY_DNS.md](./GODADDY_DNS.md) pour plus de détails.

## 🔒 Obtenir les certificats SSL

```bash
# Installer Certbot
sudo apt install certbot

# Arrêter les services temporairement
docker compose -f docker-compose.prod.yml down

# Obtenir les certificats
sudo certbot certonly --standalone \
  -d legrimoireonline.ca \
  -d www.legrimoireonline.ca

# Copier les certificats
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/
sudo chown legrimoire:legrimoire nginx/ssl/*
```

## 📊 Monitoring

### Vérifier les services

```bash
# Statut des conteneurs
docker compose -f docker-compose.prod.yml ps

# Logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Utilisation des ressources
docker stats

# Espace disque
df -h
```

### Points à surveiller

- **CPU/RAM** : Devrait rester sous 80% en utilisation normale
- **Disque** : Nettoyer les anciennes sauvegardes si >80%
- **Logs** : Vérifier les erreurs quotidiennement
- **SSL** : Renouveler avant expiration (automatique avec certbot)

## 🔄 Mises à jour

### Mise à jour de l'application

```bash
cd ~/apps/le-grimoire

# Créer une sauvegarde
./deploy.sh backup

# Mettre à jour le code
git pull origin main

# Reconstruire et redémarrer
./deploy.sh update
```

### Mise à jour du système

```bash
# Mise à jour des paquets
sudo apt update && sudo apt upgrade -y

# Redémarrer si nécessaire
sudo reboot
```

## 💾 Sauvegardes

### Sauvegardes automatiques

Configurez un cron job pour des sauvegardes quotidiennes :

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne (backup à 3h du matin)
0 3 * * * /home/legrimoire/apps/le-grimoire/backup.sh >> /home/legrimoire/apps/le-grimoire/backups/backup.log 2>&1
```

### Sauvegarde manuelle

```bash
./deploy.sh backup
```

Les sauvegardes sont stockées dans `backups/` avec le format :
`mongodb_backup_YYYYMMDD_HHMMSS.tar.gz`

## 🆘 Dépannage

### Le site n'est pas accessible

1. Vérifier le DNS : `nslookup legrimoireonline.ca`
2. Vérifier les conteneurs : `docker compose -f docker-compose.prod.yml ps`
3. Vérifier les logs : `docker compose -f docker-compose.prod.yml logs nginx`
4. Vérifier le pare-feu : `sudo ufw status`

### Erreur SSL

1. Vérifier les certificats : `ls -la nginx/ssl/`
2. Recopier les certificats si nécessaire
3. Redémarrer nginx : `docker compose -f docker-compose.prod.yml restart nginx`

### Base de données inaccessible

1. Vérifier MongoDB : `docker compose -f docker-compose.prod.yml logs mongodb`
2. Vérifier la connexion : `docker compose -f docker-compose.prod.yml exec mongodb mongosh`
3. Redémarrer MongoDB : `docker compose -f docker-compose.prod.yml restart mongodb`

Pour plus de solutions, voir [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md#dépannage).

## 📞 Support

- **Documentation** : [docs/README.md](../README.md)
- **Issues GitHub** : https://github.com/sparck75/le-grimoire/issues
- **Support Vultr** : https://my.vultr.com/support/
- **Support GoDaddy** : https://www.godaddy.com/contact-us

## ✅ Checklist de déploiement

### Avant le déploiement
- [ ] Serveur Vultr créé
- [ ] DNS configuré sur GoDaddy
- [ ] Propagation DNS vérifiée (whatsmydns.net)
- [ ] Accès SSH configuré

### Configuration du serveur
- [ ] Utilisateur non-root créé
- [ ] Pare-feu UFW configuré
- [ ] Docker installé
- [ ] Clés SSH configurées

### Déploiement
- [ ] Dépôt cloné
- [ ] .env.production configuré
- [ ] Certificats SSL obtenus
- [ ] Application déployée
- [ ] Tests effectués

### Post-déploiement
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring mis en place
- [ ] Documentation lue
- [ ] Plan d'urgence préparé

## 🎉 Succès !

Une fois le déploiement terminé, votre application devrait être accessible sur :

- **Site principal** : https://legrimoireonline.ca
- **Avec www** : https://www.legrimoireonline.ca
- **Documentation API** : https://legrimoireonline.ca/docs

Félicitations ! 🎊
