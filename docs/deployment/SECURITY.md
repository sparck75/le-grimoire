# Guide de sécurité - Le Grimoire Production

Ce document contient les meilleures pratiques de sécurité pour le déploiement et la maintenance de Le Grimoire en production.

## 🔐 Configuration du serveur

### Utilisateur non-root

✅ **À faire** :
- Toujours utiliser un utilisateur non-root pour les opérations quotidiennes
- Utiliser `sudo` uniquement quand nécessaire
- Ne jamais exécuter Docker en tant que root sans le groupe docker

❌ **À éviter** :
- Se connecter directement en tant que root
- Donner des permissions sudo illimitées
- Partager les identifiants de connexion

### Authentification SSH

✅ **À faire** :
- Utiliser l'authentification par clé SSH (pas de mot de passe)
- Utiliser des clés ed25519 ou RSA 4096 bits
- Protéger vos clés privées avec une phrase de passe
- Désactiver l'authentification par mot de passe dans `/etc/ssh/sshd_config`
- Désactiver la connexion root : `PermitRootLogin no`
- Changer le port SSH (optionnel mais recommandé) : `Port 2222`

❌ **À éviter** :
- Utiliser des mots de passe faibles
- Laisser les clés privées sans protection
- Partager les clés SSH
- Laisser PermitRootLogin à yes

### Pare-feu (UFW)

✅ **Configuration minimale** :

```bash
# Autoriser SSH
sudo ufw allow OpenSSH

# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le pare-feu
sudo ufw enable

# Vérifier le statut
sudo ufw status verbose
```

❌ **À éviter** :
- Ouvrir tous les ports : `ufw allow 1:65535/tcp`
- Exposer les ports de base de données (27017, 5432) publiquement
- Oublier d'activer le pare-feu

## 🔒 Secrets et variables d'environnement

### Gestion des secrets

✅ **À faire** :
- Générer des clés secrètes fortes et aléatoires
- Stocker les secrets dans `.env.production` (jamais dans Git)
- Utiliser des gestionnaires de mots de passe (LastPass, 1Password, Bitwarden)
- Faire une sauvegarde sécurisée de `.env.production`
- Changer les secrets régulièrement (tous les 6 mois minimum)

```bash
# Générer des secrets forts
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

❌ **À éviter** :
- Utiliser des secrets faibles comme "secret123"
- Commiter `.env.production` dans Git
- Partager les secrets par email ou chat non chiffré
- Utiliser les mêmes secrets en dev et prod

### Mots de passe des bases de données

✅ **À faire** :
- Utiliser des mots de passe d'au moins 32 caractères
- Inclure lettres majuscules, minuscules, chiffres et caractères spéciaux
- Utiliser des mots de passe différents pour chaque service
- Changer les mots de passe par défaut immédiatement

❌ **À éviter** :
- Utiliser des mots de passe courts (<16 caractères)
- Réutiliser des mots de passe
- Utiliser des mots de passe prévisibles

## 🌐 Configuration Nginx

### Headers de sécurité

✅ **Déjà configurés dans `nginx.prod.conf`** :

```nginx
# Protection contre le clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Protection contre le MIME sniffing
add_header X-Content-Type-Options "nosniff" always;

# Protection XSS
add_header X-XSS-Protection "1; mode=block" always;

# Politique de référent
add_header Referrer-Policy "no-referrer-when-downgrade" always;

# HSTS (force HTTPS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### SSL/TLS

✅ **À faire** :
- Utiliser Let's Encrypt pour les certificats SSL gratuits
- Renouveler les certificats automatiquement
- Utiliser TLS 1.2 et TLS 1.3 uniquement
- Tester votre configuration SSL : https://www.ssllabs.com/ssltest/

❌ **À éviter** :
- Utiliser des certificats auto-signés en production
- Oublier de renouveler les certificats
- Utiliser des protocoles obsolètes (TLS 1.0, TLS 1.1)

### Rate Limiting

✅ **Déjà configuré** :
- API : 10 requêtes/seconde
- Général : 30 requêtes/seconde

Ajustez selon vos besoins dans `nginx.prod.conf`.

## 🗄️ Sécurité des bases de données

### MongoDB

✅ **À faire** :
- Activer l'authentification (déjà fait)
- Ne pas exposer le port 27017 publiquement
- Créer des utilisateurs avec des permissions limitées
- Chiffrer les sauvegardes
- Faire des sauvegardes régulières

❌ **À éviter** :
- Utiliser l'utilisateur root MongoDB pour l'application
- Exposer MongoDB sans authentification
- Oublier de faire des sauvegardes

### PostgreSQL (si utilisé)

✅ **À faire** :
- Utiliser des mots de passe forts
- Limiter les connexions à localhost
- Activer SSL pour les connexions distantes
- Faire des sauvegardes régulières

## 🔄 Mises à jour et maintenance

### Mises à jour système

✅ **À faire** :

```bash
# Mettre à jour régulièrement (au moins une fois par semaine)
sudo apt update
sudo apt upgrade -y

# Mettre à jour les packages de sécurité automatiquement
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Mises à jour Docker

✅ **À faire** :

```bash
# Mettre à jour les images Docker régulièrement
cd ~/apps/le-grimoire
./deploy.sh update

# Nettoyer les anciennes images
docker system prune -a
```

### Surveillance

✅ **À faire** :
- Surveiller les logs régulièrement : `docker compose logs -f`
- Surveiller l'utilisation du disque : `df -h`
- Surveiller l'utilisation CPU/RAM : `htop`
- Configurer des alertes (optionnel : Grafana, Prometheus)

## 💾 Sauvegardes

### Stratégie de sauvegarde

✅ **À faire** :
- Sauvegardes automatiques quotidiennes (configuré avec cron)
- Garder au moins 7 jours de sauvegardes
- Tester la restauration régulièrement
- Stocker les sauvegardes hors site (Vultr Object Storage, S3, etc.)

```bash
# Sauvegarde manuelle
cd ~/apps/le-grimoire
./deploy.sh backup

# Ou avec le script
./backup.sh
```

### Restauration

✅ **Procédure de test** :

```bash
# Extraire le backup
cd ~/apps/le-grimoire/backups
tar -xzf mongodb_backup_YYYYMMDD_HHMMSS.tar.gz

# Restaurer dans MongoDB
docker exec -i le-grimoire-mongodb-prod mongorestore \
  --authenticationDatabase admin \
  -u legrimoire \
  -p "VOTRE_MOT_DE_PASSE" \
  /tmp/restore/

# Copier les fichiers dans le conteneur
docker cp mongodb_backup_YYYYMMDD_HHMMSS/legrimoire \
  le-grimoire-mongodb-prod:/tmp/restore/
```

## 📊 Logs et monitoring

### Logs

✅ **À faire** :
- Consulter les logs régulièrement
- Configurer la rotation des logs
- Surveiller les erreurs et warnings

```bash
# Voir tous les logs
docker compose -f docker-compose.prod.yml logs

# Voir les logs d'un service
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs backend

# Suivre les logs en temps réel
docker compose -f docker-compose.prod.yml logs -f
```

### Rotation des logs Docker

```bash
# Créer ou éditer /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json
```

Contenu :

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
# Redémarrer Docker
sudo systemctl restart docker
```

## 🚨 Réponse aux incidents

### En cas de compromission

1. **Isoler le serveur** :
   ```bash
   sudo ufw deny from any
   ```

2. **Analyser les logs** :
   ```bash
   # Voir les connexions SSH
   sudo grep "Accepted" /var/log/auth.log
   
   # Voir les connexions actives
   who
   
   # Voir les processus suspects
   ps aux | grep -v grep
   ```

3. **Changer tous les mots de passe** :
   - Mots de passe utilisateur
   - Clés SSH
   - Secrets de l'application
   - Mots de passe des bases de données

4. **Restaurer depuis une sauvegarde propre**

5. **Investiguer la cause** :
   - Analyser les logs
   - Vérifier les fichiers modifiés
   - Chercher des backdoors

### Contacts d'urgence

- Support Vultr : https://my.vultr.com/support/
- Support GoDaddy : https://www.godaddy.com/contact-us
- Communauté Docker : https://forums.docker.com/

## ✅ Checklist de sécurité

### Configuration initiale
- [ ] Utilisateur non-root créé
- [ ] SSH configuré avec clés (pas de mot de passe)
- [ ] Connexion root SSH désactivée
- [ ] Pare-feu UFW activé et configuré
- [ ] Fail2ban installé (optionnel mais recommandé)
- [ ] Mises à jour automatiques activées

### Application
- [ ] Secrets forts générés pour .env.production
- [ ] Certificats SSL installés (Let's Encrypt)
- [ ] HTTPS obligatoire (redirection HTTP → HTTPS)
- [ ] Headers de sécurité configurés
- [ ] Rate limiting activé
- [ ] CORS configuré correctement

### Bases de données
- [ ] Authentification MongoDB activée
- [ ] Ports de base de données non exposés publiquement
- [ ] Mots de passe forts pour toutes les bases de données
- [ ] Sauvegardes automatiques configurées
- [ ] Procédure de restauration testée

### Monitoring
- [ ] Logs vérifiés régulièrement
- [ ] Rotation des logs configurée
- [ ] Utilisation des ressources surveillée
- [ ] Alertes configurées (optionnel)

### Maintenance
- [ ] Mises à jour système régulières
- [ ] Mises à jour Docker régulières
- [ ] Sauvegardes testées mensuellement
- [ ] Plan de réponse aux incidents documenté

## 📚 Ressources supplémentaires

- [Guide de sécurité Ubuntu](https://ubuntu.com/security)
- [Guide de sécurité Docker](https://docs.docker.com/engine/security/)
- [Guide de sécurité Nginx](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Note importante** : La sécurité est un processus continu, pas un état final. Restez informé des nouvelles vulnérabilités et mettez à jour vos systèmes régulièrement.
