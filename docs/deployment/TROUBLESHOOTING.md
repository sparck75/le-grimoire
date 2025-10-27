# Guide de Dépannage - Déploiement Le Grimoire

Ce guide vous aide à résoudre les problèmes courants lors du déploiement de Le Grimoire.

## 📋 Table des matières

- [Problèmes DNS](#problèmes-dns)
- [Problèmes SSL/TLS](#problèmes-ssltls)
- [Problèmes Docker](#problèmes-docker)
- [Problèmes de connexion](#problèmes-de-connexion)
- [Problèmes de base de données](#problèmes-de-base-de-données)
- [Problèmes de performance](#problèmes-de-performance)
- [Problèmes d'accès](#problèmes-daccès)

---

## Problèmes DNS

### Le domaine ne pointe pas vers mon serveur

**Symptômes** :
- Le domaine affiche "This site can't be reached" ou "DNS_PROBE_FINISHED_NXDOMAIN"
- `nslookup legrimoireonline.ca` ne retourne pas votre IP Vultr

**Diagnostic** :
```bash
# Vérifier la résolution DNS
nslookup legrimoireonline.ca

# Ou avec dig
dig legrimoireonline.ca
```

**Solutions** :

1. **Vérifier la configuration GoDaddy**
   - Allez sur GoDaddy → My Products → legrimoireonline.ca → DNS
   - Vérifiez que l'enregistrement A pour "@" pointe vers votre IP Vultr
   - Vérifiez que l'enregistrement A/CNAME pour "www" existe

2. **Attendre la propagation**
   - La propagation DNS peut prendre 15 minutes à 48 heures
   - Testez avec https://dnschecker.org/?type=A&query=legrimoireonline.ca
   - Vérifiez depuis plusieurs localisations

3. **Vider le cache DNS**
   ```bash
   # Windows
   ipconfig /flushdns
   
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   ```

4. **Vérifier les Nameservers**
   - Sur GoDaddy DNS Management, section "Nameservers"
   - Doit être sur "GoDaddy Nameservers" (pas Custom)
   - Si vous avez changé de nameservers, attendez 24-48h

---

### www ne fonctionne pas mais le domaine principal oui

**Symptômes** :
- https://legrimoireonline.ca fonctionne
- https://www.legrimoireonline.ca ne fonctionne pas

**Solutions** :

1. **Ajouter l'enregistrement www dans GoDaddy**
   ```
   Type: A
   Name: www
   Value: VOTRE_IP_VULTR
   TTL: 600
   ```

2. **Ou utiliser un CNAME**
   ```
   Type: CNAME
   Name: www
   Value: legrimoireonline.ca
   TTL: 3600
   ```

3. **Vérifier nginx**
   ```bash
   # Vérifier que nginx écoute pour www
   docker compose -f docker-compose.prod.yml exec nginx nginx -T | grep server_name
   
   # Devrait montrer : server_name legrimoireonline.ca www.legrimoireonline.ca;
   ```

---

## Problèmes SSL/TLS

### Certificat SSL invalide ou expiré

**Symptômes** :
- Erreur "Your connection is not private" / "NET::ERR_CERT_AUTHORITY_INVALID"
- Navigateur affiche un avertissement de sécurité

**Diagnostic** :
```bash
# Vérifier les certificats
certbot certificates

# Vérifier les fichiers
ls -l nginx/ssl/

# Tester SSL
openssl s_client -connect legrimoireonline.ca:443 -servername legrimoireonline.ca
```

**Solutions** :

1. **Vérifier que les certificats existent**
   ```bash
   ls -l /etc/letsencrypt/live/legrimoireonline.ca/
   ```

2. **Réobtenir le certificat**
   ```bash
   # Arrêter nginx
   docker compose -f docker-compose.prod.yml stop nginx
   
   # Supprimer l'ancien certificat
   rm -rf /etc/letsencrypt/live/legrimoireonline.ca/
   rm -rf /etc/letsencrypt/archive/legrimoireonline.ca/
   rm -rf /etc/letsencrypt/renewal/legrimoireonline.ca.conf
   
   # Obtenir un nouveau certificat
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

3. **Vérifier les permissions**
   ```bash
   chmod 644 nginx/ssl/fullchain.pem
   chmod 600 nginx/ssl/privkey.pem
   ```

---

### Erreur "too many certificates already issued"

**Symptômes** :
- Certbot échoue avec "too many certificates already issued for exact set of domains"

**Cause** :
- Let's Encrypt limite à 5 certificats par semaine pour le même domaine

**Solutions** :

1. **Attendre une semaine** avant de réessayer

2. **Utiliser staging environment pour tester**
   ```bash
   certbot certonly --standalone --staging \
     -d legrimoireonline.ca -d www.legrimoireonline.ca \
     --email votre-email@example.com \
     --agree-tos --non-interactive
   ```

3. **Vérifier les certificats existants**
   ```bash
   certbot certificates
   ```

---

### Le renouvellement automatique ne fonctionne pas

**Diagnostic** :
```bash
# Tester le renouvellement
certbot renew --dry-run

# Vérifier le cron
crontab -l | grep renew

# Vérifier les logs
cat /var/log/ssl-renewal.log
```

**Solutions** :

1. **Vérifier le script de renouvellement**
   ```bash
   cat /root/renew-ssl.sh
   chmod +x /root/renew-ssl.sh
   ```

2. **Tester manuellement**
   ```bash
   /root/renew-ssl.sh
   ```

3. **Reconfigurer le cron**
   ```bash
   (crontab -l 2>/dev/null; echo "0 3 * * 1 /root/renew-ssl.sh") | crontab -
   ```

---

## Problèmes Docker

### Les conteneurs ne démarrent pas

**Diagnostic** :
```bash
# Voir l'état des conteneurs
docker compose -f docker-compose.prod.yml ps

# Voir les logs
docker compose -f docker-compose.prod.yml logs
```

**Solutions** :

1. **Vérifier les logs d'un service spécifique**
   ```bash
   docker compose -f docker-compose.prod.yml logs frontend
   docker compose -f docker-compose.prod.yml logs backend
   docker compose -f docker-compose.prod.yml logs mongodb
   ```

2. **Redémarrer un service**
   ```bash
   docker compose -f docker-compose.prod.yml restart frontend
   ```

3. **Reconstruire les images**
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml build --no-cache
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Vérifier le fichier .env**
   ```bash
   cat .env
   # Assurez-vous que toutes les variables sont définies
   ```

---

### Erreur "port already in use"

**Symptômes** :
- "bind: address already in use"

**Diagnostic** :
```bash
# Voir ce qui utilise le port 80
sudo lsof -i :80

# Voir ce qui utilise le port 443
sudo lsof -i :443
```

**Solutions** :

1. **Arrêter le service conflictuel**
   ```bash
   # Si c'est Apache
   sudo systemctl stop apache2
   sudo systemctl disable apache2
   
   # Si c'est un autre nginx
   sudo systemctl stop nginx
   sudo systemctl disable nginx
   ```

2. **Changer les ports dans docker-compose.prod.yml**
   ```yaml
   ports:
     - "8080:80"  # Au lieu de 80:80
     - "8443:443" # Au lieu de 443:443
   ```

---

### Espace disque insuffisant

**Symptômes** :
- "no space left on device"
- Les conteneurs s'arrêtent de manière aléatoire

**Diagnostic** :
```bash
# Vérifier l'espace disque
df -h

# Voir l'utilisation Docker
docker system df
```

**Solutions** :

1. **Nettoyer Docker**
   ```bash
   # Supprimer les images non utilisées
   docker image prune -a
   
   # Supprimer les volumes non utilisés
   docker volume prune
   
   # Tout nettoyer (ATTENTION : supprime tout ce qui n'est pas utilisé)
   docker system prune -a --volumes
   ```

2. **Supprimer les logs volumineux**
   ```bash
   # Trouver les gros fichiers de logs
   find /var/lib/docker/containers -name "*.log" -size +100M
   
   # Supprimer les logs
   truncate -s 0 /var/lib/docker/containers/*/*-json.log
   ```

3. **Upgrader le serveur** avec plus d'espace disque

---

## Problèmes de connexion

### Impossible de se connecter au serveur SSH

**Symptômes** :
- "Connection refused" ou "Connection timed out"

**Solutions** :

1. **Vérifier que le serveur est allumé**
   - Sur Vultr dashboard, vérifier l'état du serveur

2. **Vérifier l'IP**
   ```bash
   # Pinger le serveur
   ping VOTRE_IP_VULTR
   ```

3. **Vérifier le pare-feu**
   ```bash
   # Sur le serveur
   sudo ufw status
   
   # SSH doit être autorisé
   sudo ufw allow OpenSSH
   ```

4. **Réinitialiser le mot de passe root**
   - Sur Vultr dashboard → Server → Settings → Root Password

---

### "Permission denied" lors de la connexion SSH

**Solutions** :

1. **Vérifier le nom d'utilisateur**
   ```bash
   # Connectez-vous en tant que root
   ssh root@VOTRE_IP_VULTR
   ```

2. **Vérifier la clé SSH**
   ```bash
   # Vérifier que la clé est chargée
   ssh-add -l
   
   # Ajouter la clé
   ssh-add ~/.ssh/votre_cle
   ```

3. **Utiliser le mot de passe**
   ```bash
   ssh -o PreferredAuthentications=password root@VOTRE_IP_VULTR
   ```

---

## Problèmes de base de données

### MongoDB ne démarre pas

**Diagnostic** :
```bash
# Voir les logs MongoDB
docker compose -f docker-compose.prod.yml logs mongodb
```

**Solutions courantes** :

1. **Vérifier l'espace disque**
   ```bash
   df -h
   ```

2. **Vérifier les permissions**
   ```bash
   # Voir les volumes Docker
   docker volume ls
   
   # Inspecter le volume MongoDB
   docker volume inspect le-grimoire_mongodb_data
   ```

3. **Réinitialiser MongoDB (ATTENTION : perte de données)**
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker volume rm le-grimoire_mongodb_data
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Restaurer depuis une sauvegarde**
   ```bash
   docker cp ./backup-20240115 le-grimoire-mongodb:/backup
   docker exec le-grimoire-mongodb mongorestore \
     --username=legrimoire \
     --password=VOTRE_PASSWORD \
     --authenticationDatabase=admin \
     --db=legrimoire /backup/legrimoire
   ```

---

### Pas d'ingrédients dans la base de données

**Diagnostic** :
```bash
# Compter les ingrédients
docker compose -f docker-compose.prod.yml exec mongodb mongosh \
  -u legrimoire -p VOTRE_PASSWORD --authenticationDatabase admin \
  --eval "use legrimoire; db.ingredients.countDocuments()"
```

**Solutions** :

1. **Importer les ingrédients**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend \
     python scripts/import_openfoodfacts.py
   ```

2. **Vérifier que le fichier existe**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend \
     ls -la data/openfoodfacts/
   ```

---

## Problèmes de performance

### Le site est lent

**Diagnostic** :
```bash
# Vérifier les ressources
docker stats

# Voir l'utilisation CPU/RAM
htop

# Voir l'espace disque
df -h

# Voir l'utilisation réseau
iftop
```

**Solutions** :

1. **Vérifier les logs pour les erreurs**
   ```bash
   docker compose -f docker-compose.prod.yml logs --tail=100
   ```

2. **Redémarrer les services**
   ```bash
   docker compose -f docker-compose.prod.yml restart
   ```

3. **Optimiser MongoDB**
   ```bash
   # Créer des index
   docker compose -f docker-compose.prod.yml exec mongodb mongosh \
     -u legrimoire -p VOTRE_PASSWORD --authenticationDatabase admin \
     --eval "use legrimoire; db.ingredients.createIndex({'names.fr': 1})"
   ```

4. **Upgrader le serveur Vultr**
   - Passer à un plan avec plus de CPU/RAM

5. **Configurer un CDN** (Cloudflare)
   - Réduire la charge sur le serveur
   - Améliorer les performances globales

---

### RAM saturée (Out of Memory)

**Symptômes** :
- Conteneurs qui s'arrêtent de manière aléatoire
- Serveur très lent

**Diagnostic** :
```bash
# Voir l'utilisation de la RAM
free -h

# Voir quelle application utilise le plus de RAM
docker stats --no-stream
```

**Solutions** :

1. **Limiter la RAM des conteneurs**
   
   Modifier `docker-compose.prod.yml` :
   ```yaml
   frontend:
     # ...
     deploy:
       resources:
         limits:
           memory: 512M
   
   backend:
     # ...
     deploy:
       resources:
         limits:
           memory: 1G
   ```

2. **Ajouter du swap**
   ```bash
   # Créer un fichier swap de 2GB
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # Rendre permanent
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

3. **Upgrader le serveur** vers un plan avec plus de RAM

---

## Problèmes d'accès

### Erreur 502 Bad Gateway

**Cause** :
- Le backend ne répond pas
- Nginx ne peut pas se connecter au frontend/backend

**Solutions** :

1. **Vérifier que les conteneurs sont actifs**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

2. **Vérifier les logs**
   ```bash
   docker compose -f docker-compose.prod.yml logs frontend
   docker compose -f docker-compose.prod.yml logs backend
   docker compose -f docker-compose.prod.yml logs nginx
   ```

3. **Redémarrer les services**
   ```bash
   docker compose -f docker-compose.prod.yml restart frontend backend
   ```

4. **Vérifier la configuration nginx**
   ```bash
   docker compose -f docker-compose.prod.yml exec nginx nginx -t
   ```

---

### Erreur 504 Gateway Timeout

**Cause** :
- Le backend met trop de temps à répondre

**Solutions** :

1. **Augmenter le timeout nginx**
   
   Dans `nginx/nginx.prod.conf`, ajouter :
   ```nginx
   proxy_connect_timeout 600;
   proxy_send_timeout 600;
   proxy_read_timeout 600;
   send_timeout 600;
   ```

2. **Vérifier les performances du backend**
   ```bash
   docker compose -f docker-compose.prod.yml logs backend | tail -100
   ```

---

### Impossible d'uploader des images

**Symptômes** :
- Erreur lors de l'upload d'images
- Images ne s'affichent pas

**Solutions** :

1. **Vérifier la taille maximale**
   
   Dans `nginx/nginx.prod.conf` :
   ```nginx
   client_max_body_size 20M;
   ```

2. **Vérifier les permissions du volume**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend ls -la /app/uploads
   docker compose -f docker-compose.prod.yml exec backend chmod 777 /app/uploads
   ```

3. **Vérifier l'espace disque**
   ```bash
   df -h
   ```

---

## Commandes de diagnostic utiles

### Vérifier l'état général

```bash
# État des conteneurs
docker compose -f docker-compose.prod.yml ps

# Logs de tous les services
docker compose -f docker-compose.prod.yml logs --tail=50

# Ressources utilisées
docker stats --no-stream

# Espace disque
df -h

# RAM
free -h

# Processus
htop
```

### Vérifier la connectivité

```bash
# Depuis le serveur, tester l'accès au frontend
curl -I http://localhost:3000

# Tester l'accès au backend
curl http://localhost:8000/health

# Tester depuis l'extérieur
curl -I https://legrimoireonline.ca
```

### Nettoyer complètement et redémarrer

```bash
cd /root/apps/le-grimoire

# Arrêter tout
docker compose -f docker-compose.prod.yml down

# Nettoyer Docker
docker system prune -a

# Reconstruire
docker compose -f docker-compose.prod.yml build --no-cache

# Redémarrer
docker compose -f docker-compose.prod.yml up -d

# Vérifier
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

---

## 📞 Besoin d'aide supplémentaire ?

Si votre problème n'est pas résolu :

1. **Consultez les logs détaillés**
   ```bash
   docker compose -f docker-compose.prod.yml logs --tail=1000 > logs.txt
   ```

2. **Ouvrez une issue sur GitHub**
   - https://github.com/sparck75/le-grimoire/issues
   - Incluez :
     - Description du problème
     - Messages d'erreur
     - Logs pertinents
     - Configuration (sans mots de passe!)

3. **Ressources externes**
   - [Vultr Support](https://www.vultr.com/docs/)
   - [Docker Documentation](https://docs.docker.com/)
   - [Nginx Documentation](https://nginx.org/en/docs/)
   - [Let's Encrypt Community](https://community.letsencrypt.org/)
   - [Stack Overflow](https://stackoverflow.com/)

---

**Bon courage avec votre déploiement ! 🚀**
