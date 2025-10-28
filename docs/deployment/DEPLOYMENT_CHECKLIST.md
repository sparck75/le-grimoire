# Checklist de Déploiement - Le Grimoire

Utilisez cette checklist pour suivre votre progression lors du déploiement de Le Grimoire sur Vultr avec le domaine legrimoireonline.ca.

**Durée estimée** : 2-3 heures (incluant la propagation DNS)

---

## ✅ Préparation (10 minutes)

- [ ] Compte Vultr créé et vérifié
- [ ] Domaine **legrimoireonline.ca** enregistré chez GoDaddy
- [ ] Accès à votre compte GoDaddy
- [ ] Client SSH installé sur votre ordinateur
- [ ] Git installé localement
- [ ] Adresse email valide pour Let's Encrypt

**Notes** :
- IP Vultr : `___________________________`
- Email Let's Encrypt : `___________________________`

---

## 🖥️ Configuration Serveur Vultr (15 minutes)

### Création du serveur

- [ ] Connecté à https://my.vultr.com/
- [ ] Cliqué sur "Deploy New Server"
- [ ] Type : **Cloud Compute** sélectionné
- [ ] Localisation : **Toronto, Canada** (ou New York/Atlanta)
- [ ] Image : **Ubuntu 22.04 LTS x64**
- [ ] Plan sélectionné :
  - [ ] 2 vCPU, 4 GB RAM, 80 GB SSD ($18/mois) - Minimum
  - [ ] 2 vCPU, 4 GB RAM, 100 GB SSD ($24/mois) - Recommandé
  - [ ] 4 vCPU, 8 GB RAM, 160 GB SSD ($48/mois) - Haute performance
- [ ] IPv6 activé
- [ ] Auto Backups activé ($1.50/mois - recommandé)
- [ ] Clé SSH ajoutée OU mot de passe root noté
- [ ] Hostname : `legrimoire-prod`
- [ ] Label : `Le Grimoire Production`
- [ ] Serveur déployé avec succès

### Information du serveur

- [ ] Adresse IP notée : `___________________________`
- [ ] IPv6 notée (optionnel) : `___________________________`
- [ ] Mot de passe root noté (si pas de clé SSH)

### Connexion initiale

- [ ] Connexion SSH testée : `ssh root@VOTRE_IP`
- [ ] Connexion réussie

---

## 📦 Installation des Dépendances (15 minutes)

### Mise à jour système

```bash
apt update && apt upgrade -y
apt install -y curl wget git vim ufw htop
```

- [ ] Système mis à jour
- [ ] Outils de base installés

### Configuration pare-feu UFW

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

- [ ] SSH autorisé (port 22)
- [ ] HTTP autorisé (port 80)
- [ ] HTTPS autorisé (port 443)
- [ ] Pare-feu activé
- [ ] Statut vérifié

### Installation Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
docker --version
```

- [ ] Docker installé
- [ ] Version vérifiée : `___________________________`

### Installation Docker Compose

```bash
# Docker Compose est installé automatiquement comme plugin avec Docker
# Si ce n'est pas le cas, l'installer manuellement:
sudo apt install -y docker-compose-plugin

# Vérifier l'installation
docker compose version
```

- [ ] Docker Compose installé
- [ ] Version vérifiée : `___________________________`

### Créer utilisateur non-root (optionnel mais recommandé)

```bash
adduser legrimoire
usermod -aG sudo legrimoire
usermod -aG docker legrimoire
```

- [ ] Utilisateur `legrimoire` créé
- [ ] Ajouté au groupe sudo
- [ ] Ajouté au groupe docker
- [ ] Connexion testée : `su - legrimoire`

---

## 🌐 Configuration DNS GoDaddy (30 minutes - incluant propagation)

### Connexion GoDaddy

- [ ] Connecté à https://godaddy.com/
- [ ] Accès à **My Products**
- [ ] Domaine **legrimoireonline.ca** trouvé
- [ ] Page **DNS Management** ouverte

### Suppression enregistrements existants

- [ ] Enregistrement A pour "@" supprimé (s'il pointait vers GoDaddy)
- [ ] Enregistrement CNAME pour "www" supprimé (s'il existait)
- [ ] Autres enregistrements A inutiles supprimés

**Important** : Ne supprimez PAS les enregistrements NS, SOA, MX, ou TXT

### Ajout nouveaux enregistrements

**Enregistrement A principal** :
- [ ] Type : **A**
- [ ] Name : **@**
- [ ] Value : `VOTRE_IP_VULTR` (`___________________________`)
- [ ] TTL : **600 seconds**
- [ ] Enregistrement sauvegardé

**Enregistrement A pour www** :
- [ ] Type : **A**
- [ ] Name : **www**
- [ ] Value : `VOTRE_IP_VULTR` (`___________________________`)
- [ ] TTL : **600 seconds**
- [ ] Enregistrement sauvegardé

**Alternative - Enregistrement CNAME pour www** (choisir A OU CNAME, pas les deux) :
- [ ] Type : **CNAME**
- [ ] Name : **www**
- [ ] Value : **legrimoireonline.ca**
- [ ] TTL : **1 hour**
- [ ] Enregistrement sauvegardé

### Vérification DNS

- [ ] Nameservers sur "GoDaddy Nameservers" (pas Custom)
- [ ] Configuration DNS sauvegardée
- [ ] `nslookup legrimoireonline.ca` lancé
- [ ] Résolution DNS testée sur https://dnschecker.org/
- [ ] Propagation en cours (15 min - 48h)

**Note** : Vous pouvez continuer pendant la propagation, mais attendez avant d'obtenir le certificat SSL.

---

## 🚀 Déploiement Application (20 minutes)

### Clonage du dépôt

```bash
mkdir -p /root/apps && cd /root/apps
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
```

- [ ] Répertoire `/root/apps` créé
- [ ] Dépôt cloné
- [ ] Dans le répertoire `le-grimoire`

### Création fichier .env

```bash
cp .env.production.template .env
nano .env
```

- [ ] Fichier `.env` créé depuis le template
- [ ] Variables modifiées :

**Mots de passe** :
- [ ] `MONGODB_USER` : `legrimoire` (par défaut)
- [ ] `MONGODB_PASSWORD` changé : `___________________________`
- [ ] `MONGODB_URL` mis à jour avec le bon mot de passe
- [ ] `POSTGRES_PASSWORD` changé : `___________________________`

**Secrets générés** :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```
- [ ] `SECRET_KEY` généré : `___________________________` (premiers chars)
- [ ] `JWT_SECRET_KEY` généré : `___________________________` (premiers chars)

**URLs** :
- [ ] `NEXT_PUBLIC_API_URL=https://legrimoireonline.ca`
- [ ] `BACKEND_URL=http://backend:8000`

**OAuth (optionnel)** :
- [ ] `GOOGLE_CLIENT_ID` configuré (si applicable)
- [ ] `GOOGLE_CLIENT_SECRET` configuré (si applicable)
- [ ] `APPLE_CLIENT_ID` configuré (si applicable)
- [ ] `APPLE_CLIENT_SECRET` configuré (si applicable)

- [ ] Fichier `.env` sauvegardé

### Configuration Nginx

Vérifier que `nginx/nginx.prod.conf` existe et contient :
```nginx
server_name legrimoireonline.ca www.legrimoireonline.ca;
```

- [ ] Fichier `nginx/nginx.prod.conf` vérifié
- [ ] `server_name` correct avec votre domaine
- [ ] Configuration HTTPS présente (ports 443)
- [ ] Redirection HTTP → HTTPS présente

### Certificats SSL temporaires

```bash
mkdir -p nginx/ssl certbot/www
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=CA/ST=Quebec/L=Montreal/O=LeGrimoire/CN=legrimoireonline.ca"
```

- [ ] Répertoires `nginx/ssl` et `certbot/www` créés
- [ ] Certificats temporaires générés
- [ ] Fichiers présents dans `nginx/ssl/`

### Vérification docker-compose.prod.yml

- [ ] Fichier `docker-compose.prod.yml` vérifié
- [ ] Section nginx référence `nginx.prod.conf`
- [ ] Volume certbot présent : `./certbot/www:/var/www/certbot:ro`

### Démarrage de l'application

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

- [ ] Commande lancée
- [ ] Construction des images terminée
- [ ] Conteneurs démarrés
- [ ] Aucune erreur dans la sortie

### Vérification

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs
```

- [ ] Tous les conteneurs sont "Up" :
  - [ ] le-grimoire-frontend-prod
  - [ ] le-grimoire-backend-prod
  - [ ] le-grimoire-nginx
  - [ ] le-grimoire-mongodb (ou mongodb)
  - [ ] le-grimoire-redis-prod (ou redis)
  - [ ] le-grimoire-db-prod (PostgreSQL - optionnel)
  
- [ ] Aucune erreur critique dans les logs

### Test HTTP (avant SSL)

- [ ] Ouvert `http://VOTRE_IP_VULTR` dans le navigateur
- [ ] Site s'affiche (même avec avertissement SSL)
- [ ] Testé `http://legrimoireonline.ca` (si DNS propagé)

**Note**: Cette URL sera automatiquement redirigée vers HTTPS après configuration SSL.

---

## 🔒 Configuration SSL avec Let's Encrypt (20 minutes)

**⚠️ IMPORTANT** : Attendez que le DNS soit complètement propagé avant cette étape !

### Vérification propagation DNS

```bash
nslookup legrimoireonline.ca
```

- [ ] `nslookup legrimoireonline.ca` retourne votre IP Vultr
- [ ] `nslookup www.legrimoireonline.ca` retourne votre IP Vultr
- [ ] Propagation confirmée sur https://dnschecker.org/

### Installation Certbot

```bash
apt install -y certbot
# OU
snap install --classic certbot
```

- [ ] Certbot installé
- [ ] Version vérifiée : `certbot --version`

### Obtention du certificat

```bash
docker compose -f docker-compose.prod.yml stop nginx

certbot certonly --standalone \
  -d legrimoireonline.ca -d www.legrimoireonline.ca \
  --email VOTRE_EMAIL@example.com \
  --agree-tos --non-interactive

cp /etc/letsencrypt/live/legrimoireonline.ca/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/legrimoireonline.ca/privkey.pem nginx/ssl/

docker compose -f docker-compose.prod.yml start nginx
```

- [ ] Nginx arrêté
- [ ] Commande `certbot` lancée
- [ ] Certificat obtenu avec succès
- [ ] Email de confirmation reçu de Let's Encrypt
- [ ] Certificats copiés dans `nginx/ssl/`
- [ ] Nginx redémarré
- [ ] Aucune erreur

### Vérification HTTPS

- [ ] `https://legrimoireonline.ca` fonctionne
- [ ] `https://www.legrimoireonline.ca` fonctionne
- [ ] `http://legrimoireonline.ca` redirige vers HTTPS
- [ ] Certificat valide (cadenas vert dans le navigateur)
- [ ] Pas d'avertissement de sécurité
- [ ] Testé sur https://www.ssllabs.com/ssltest/
- [ ] Note SSL Labs : `___________________________` (A ou A+ attendu)

### Configuration renouvellement automatique

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
(crontab -l 2>/dev/null; echo "0 3 * * 1 /root/renew-ssl.sh") | crontab -
```

- [ ] Script `/root/renew-ssl.sh` créé
- [ ] Script rendu exécutable
- [ ] Cron job ajouté (tous les lundis à 3h)
- [ ] Cron vérifié : `crontab -l`
- [ ] Test dry-run : `certbot renew --dry-run` ✅

---

## 💾 Configuration Finale (15 minutes)

### Initialisation MongoDB

```bash
docker compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py
```

- [ ] Script d'import lancé
- [ ] Import terminé sans erreurs
- [ ] Nombre d'ingrédients vérifié :
  ```bash
  docker compose -f docker-compose.prod.yml exec mongodb mongosh \
    -u legrimoire -p VOTRE_MONGO_PASSWORD --authenticationDatabase admin \
    --eval "use legrimoire; db.ingredients.countDocuments()"
  ```
- [ ] Résultat : **5942 ingrédients** ✅

### Création utilisateur admin (optionnel)

- [ ] Compte admin créé (si applicable)
- [ ] Credentials notés en lieu sûr

### Configuration sauvegardes automatiques

```bash
cat > /root/backup-grimoire.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/root/apps/le-grimoire"

mkdir -p $BACKUP_DIR

# MongoDB
docker exec le-grimoire-mongodb mongodump --username=legrimoire --password=VOTRE_MONGO_PASSWORD --authenticationDatabase=admin --db=legrimoire --out=/backup
docker cp le-grimoire-mongodb:/backup $BACKUP_DIR/mongodb_$DATE

# PostgreSQL (si utilisé)
# docker exec le-grimoire-db-prod pg_dump -U legrimoire_prod le_grimoire > $BACKUP_DIR/postgres_$DATE.sql

# Uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/backend/uploads 2>/dev/null || true

# Nettoyer anciens backups (garder 7 jours)
find $BACKUP_DIR -type f -mtime +7 -delete
find $BACKUP_DIR -type d -mtime +7 -delete

echo "$(date): Sauvegarde effectuée" >> /var/log/grimoire-backup.log
EOF

chmod +x /root/backup-grimoire.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /root/backup-grimoire.sh") | crontab -
```

- [ ] Script `/root/backup-grimoire.sh` créé
- [ ] Mot de passe MongoDB ajusté dans le script
- [ ] Script rendu exécutable
- [ ] Cron job ajouté (tous les jours à 2h)
- [ ] Test manuel : `/root/backup-grimoire.sh`
- [ ] Backup créé dans `/root/backups/`

### Configuration monitoring (optionnel)

```bash
cat > /root/check-grimoire.sh << 'EOF'
#!/bin/bash
cd /root/apps/le-grimoire

# Vérifier conteneurs
if [ $(docker compose -f docker-compose.prod.yml ps -q | wc -l) -lt 5 ]; then
    echo "$(date): ALERTE - Certains conteneurs sont arrêtés" >> /var/log/grimoire-monitor.log
    docker compose -f docker-compose.prod.yml up -d
fi

# Vérifier accès HTTPS
if ! curl -f -s https://legrimoireonline.ca/health > /dev/null; then
    echo "$(date): ALERTE - Site inaccessible" >> /var/log/grimoire-monitor.log
fi
EOF

chmod +x /root/check-grimoire.sh
(crontab -l 2>/dev/null; echo "*/5 * * * * /root/check-grimoire.sh") | crontab -
```

- [ ] Script `/root/check-grimoire.sh` créé
- [ ] Script rendu exécutable
- [ ] Cron job ajouté (toutes les 5 minutes)
- [ ] Logs de monitoring : `tail -f /var/log/grimoire-monitor.log`

---

## ✅ Tests Finaux (15 minutes)

### Tests de connectivité

- [ ] `https://legrimoireonline.ca` ✅
- [ ] `https://www.legrimoireonline.ca` ✅
- [ ] `http://legrimoireonline.ca` → redirige vers HTTPS ✅
- [ ] `https://legrimoireonline.ca/docs` (API documentation) ✅
- [ ] `https://legrimoireonline.ca/health` retourne "healthy" ✅

### Tests fonctionnels

- [ ] Page d'accueil s'affiche correctement
- [ ] Navigation fonctionne
- [ ] Recherche d'ingrédients fonctionne
- [ ] Création de recette testée
- [ ] Affichage des recettes fonctionne
- [ ] Upload d'image fonctionne
- [ ] Liste de courses fonctionne
- [ ] OCR fonctionne (si activé)

### Tests performance

- [ ] Temps de chargement acceptable (< 3 secondes)
- [ ] Pas d'erreurs dans la console navigateur
- [ ] Ressources serveur normales : `docker stats`
- [ ] Espace disque suffisant : `df -h`

### Vérification SSL

- [ ] Test sur https://www.ssllabs.com/ssltest/
- [ ] Note SSL : `___________________________`
- [ ] Certificat expire le : `___________________________`
- [ ] Renouvellement automatique configuré ✅

---

## 📝 Documentation et Finalisation (10 minutes)

### Documentation

- [ ] Credentials notés en lieu sûr :
  - [ ] IP serveur : `___________________________`
  - [ ] Mot de passe root : `___________________________`
  - [ ] POSTGRES_PASSWORD : `___________________________`
  - [ ] MONGO_PASSWORD : `___________________________`
  - [ ] SECRET_KEY : (premiers 20 chars) `___________________________`
  - [ ] JWT_SECRET_KEY : (premiers 20 chars) `___________________________`

- [ ] Documentation consultée :
  - [ ] [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md)
  - [ ] [GODADDY_DNS.md](./GODADDY_DNS.md)
  - [ ] [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Contacts et support

- [ ] Email enregistré chez Let's Encrypt
- [ ] Compte Vultr accessible
- [ ] Compte GoDaddy accessible
- [ ] Accès GitHub au dépôt

### Vérifications finales

- [ ] Tous les conteneurs sont "Up"
- [ ] Aucune erreur dans les logs
- [ ] Site accessible publiquement
- [ ] SSL valide
- [ ] Sauvegardes configurées
- [ ] Monitoring configuré
- [ ] Pare-feu configuré
- [ ] DNS propagé

---

## 🎉 Déploiement Terminé !

**Félicitations !** Votre application Le Grimoire est maintenant en production sur :

🌍 **https://legrimoireonline.ca**

### Informations importantes

| Information | Valeur |
|------------|--------|
| **Serveur** | Vultr - IP: `___________________________` |
| **Domaine** | legrimoireonline.ca |
| **SSL** | Let's Encrypt (renouvellement automatique) |
| **Sauvegardes** | Quotidiennes à 2h du matin |
| **Monitoring** | Toutes les 5 minutes |
| **Certificat expire** | `___________________________` |

### Prochaines étapes recommandées

- [ ] Configurer un service de monitoring externe (UptimeRobot, Pingdom)
- [ ] Mettre en place des alertes par email/SMS
- [ ] Configurer Cloudflare CDN pour améliorer les performances
- [ ] Ajouter Google Analytics
- [ ] Configurer l'envoi d'emails (SMTP)
- [ ] Activer OAuth (Google, Apple)
- [ ] Créer une page "À propos"
- [ ] Ajouter des recettes initiales
- [ ] Partager le site !

### Maintenance régulière

- **Quotidien** : Vérifier que le site fonctionne
- **Hebdomadaire** : Consulter les logs, vérifier les ressources
- **Mensuel** : Vérifier les sauvegardes, mettre à jour l'application
- **Trimestriel** : Mettre à jour le système (apt upgrade), vérifier la sécurité

### Support

- 📖 [Documentation complète](../README.md)
- 🐛 [GitHub Issues](https://github.com/sparck75/le-grimoire/issues)
- 💬 [Discussions](https://github.com/sparck75/le-grimoire/discussions)
- 📧 Support Vultr : https://www.vultr.com/support/
- 📞 Support GoDaddy : 1-800-581-0548 (Canada)

---

**Date de déploiement** : `___________________________`

**Déployé par** : `___________________________`

**Notes supplémentaires** :
```
_____________________________________________________________

_____________________________________________________________

_____________________________________________________________
```

---

**Bon courage avec Le Grimoire ! 👨‍🍳📚**
