# Documentation de Déploiement - Le Grimoire

Ce dossier contient toute la documentation nécessaire pour déployer **Le Grimoire** en production sur un serveur Vultr avec le domaine **legrimoireonline.ca**.

> 📖 **Nouveau ici ?** Lisez d'abord la [Vue d'Ensemble du Déploiement](./DEPLOYMENT_OVERVIEW.md) pour choisir le bon guide pour vous.

## 📚 Guides disponibles

### Guide rapide ⚡
**[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** - Guide en 10 étapes (45 minutes)
- Configuration serveur Vultr
- DNS GoDaddy
- Installation Docker
- Déploiement de l'application
- Configuration SSL avec Let's Encrypt

👉 **Commencez ici** si vous voulez déployer rapidement et avez déjà de l'expérience avec Linux/Docker.

---

### Guide complet 📖
**[VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md)** - Guide détaillé pas à pas (2-3 heures)
- Création et configuration du serveur Vultr (choix du plan, localisation, etc.)
- Installation des dépendances (Docker, Docker Compose, UFW)
- Configuration du pare-feu
- Déploiement de l'application
- Configuration SSL/TLS avec Let's Encrypt
- Configuration des sauvegardes automatiques
- Configuration du monitoring
- Scripts de maintenance
- Guide de dépannage complet

👉 **Lisez ce guide** si c'est votre premier déploiement ou si vous voulez tous les détails.

---

### Configuration DNS GoDaddy 🌐
**[GODADDY_DNS.md](./GODADDY_DNS.md)** - Guide spécifique GoDaddy (30 minutes)
- Instructions détaillées avec captures d'écran
- Configuration des enregistrements A et CNAME
- Vérification de la propagation DNS
- Dépannage DNS
- Temps de propagation expliqués
- Configuration email optionnelle

👉 **Consultez ce guide** pour les détails spécifiques à la configuration DNS sur GoDaddy.

---

## 🏗️ Architecture de déploiement

```
Internet
   ↓
[GoDaddy DNS]
   ↓
legrimoireonline.ca → XXX.XXX.XXX.XXX (Serveur Vultr)
   ↓
[Nginx] ← Let's Encrypt SSL/TLS
   ↓
   ├─→ [Frontend Container] (Next.js) :3000
   ├─→ [Backend Container] (FastAPI) :8000
   ├─→ [MongoDB Container] :27017
   ├─→ [PostgreSQL Container] :5432 (legacy)
   └─→ [Redis Container] :6379
```

## 📋 Checklist de déploiement

Utilisez cette checklist pour suivre votre progression :

### Préparation
- [ ] Compte Vultr créé
- [ ] Domaine legrimoireonline.ca chez GoDaddy
- [ ] Accès SSH configuré (clé ou mot de passe)
- [ ] Git installé localement

### Serveur Vultr
- [ ] Serveur créé (Ubuntu 22.04)
- [ ] IP notée : `___________________`
- [ ] Connexion SSH testée
- [ ] Système mis à jour (`apt update && apt upgrade`)
- [ ] Docker installé
- [ ] Docker Compose installé
- [ ] Pare-feu UFW configuré (ports 22, 80, 443)

### DNS GoDaddy
- [ ] Enregistrement A pour `@` créé (pointe vers IP Vultr)
- [ ] Enregistrement A/CNAME pour `www` créé
- [ ] Anciens enregistrements supprimés
- [ ] Propagation DNS vérifiée (`nslookup legrimoireonline.ca`)

### Application
- [ ] Dépôt Git cloné sur le serveur
- [ ] Fichier `.env` créé avec valeurs sécurisées
- [ ] Secrets générés (`SECRET_KEY`, `JWT_SECRET_KEY`)
- [ ] Mots de passe changés (PostgreSQL, MongoDB)
- [ ] Configuration nginx modifiée pour le domaine
- [ ] Certificats temporaires créés
- [ ] Application démarrée (`docker-compose -f docker-compose.prod.yml up -d`)
- [ ] Conteneurs actifs vérifiés
- [ ] Accès HTTP testé

### SSL/TLS
- [ ] Certbot installé
- [ ] Certificat Let's Encrypt obtenu
- [ ] Certificats copiés dans nginx/ssl
- [ ] Nginx redémarré
- [ ] Accès HTTPS testé
- [ ] Redirection HTTP → HTTPS testée
- [ ] Renouvellement automatique configuré (cron)
- [ ] Test de renouvellement effectué (`certbot renew --dry-run`)

### Configuration finale
- [ ] Ingrédients OpenFoodFacts importés (5942 items)
- [ ] Base de données MongoDB vérifiée
- [ ] Compte admin créé (si applicable)
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring configuré
- [ ] Logs vérifiés

### Tests
- [ ] https://legrimoireonline.ca fonctionne
- [ ] https://www.legrimoireonline.ca fonctionne
- [ ] http://legrimoireonline.ca redirige vers HTTPS
- [ ] https://legrimoireonline.ca/docs (API) accessible
- [ ] https://legrimoireonline.ca/health retourne "healthy"
- [ ] SSL vérifié sur https://www.ssllabs.com/ssltest/
- [ ] Création de recette testée
- [ ] Recherche d'ingrédients testée
- [ ] Liste de courses testée

## 🚀 Démarrage rapide

Pour un déploiement rapide, suivez ces étapes :

```bash
# 1. Créer le serveur sur Vultr (interface web)

# 2. Se connecter
ssh root@VOTRE_IP_VULTR

# 3. Installer Docker
curl -fsSL https://get.docker.com | sh

# 4. Installer Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 5. Cloner le projet
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire

# 6. Configurer
cp .env.production.template .env
nano .env  # Modifier les valeurs

# 7. Démarrer
docker-compose -f docker-compose.prod.yml up -d --build
```

Consultez [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) pour les détails complets.

## 🔧 Fichiers de configuration

### Fichiers importants

| Fichier | Description |
|---------|-------------|
| `.env.production.template` | Template pour les variables d'environnement de production |
| `docker-compose.prod.yml` | Configuration Docker Compose pour production |
| `nginx/nginx.prod.conf` | Configuration Nginx pour production avec SSL |
| `nginx/nginx.conf` | Configuration Nginx pour développement local |

### Créer le fichier .env

```bash
cp .env.production.template .env
nano .env
```

**Changez obligatoirement** :
- `POSTGRES_PASSWORD`
- `MONGO_INITDB_ROOT_PASSWORD`
- `SECRET_KEY` (généré avec `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `JWT_SECRET_KEY` (généré avec `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `NEXT_PUBLIC_API_URL=https://legrimoireonline.ca`

## 📊 Ressources nécessaires

### Serveur Vultr recommandé

| Plan | vCPU | RAM | SSD | Prix/mois | Usage |
|------|------|-----|-----|-----------|-------|
| **Minimum** | 1 | 2 GB | 55 GB | $12 | Développement/test |
| **Recommandé** | 2 | 4 GB | 80 GB | $18 | Production petite échelle |
| **Optimal** | 2 | 4 GB | 100 GB | $24 | Production moyenne |
| **Haute performance** | 4 | 8 GB | 160 GB | $48 | Production haute échelle |

**Recommandation** : Commencez avec le plan à **$18-24/mois** (2 vCPU, 4 GB RAM).

### Coûts totaux estimés

- **Serveur Vultr** : $18-48/mois
- **Domaine .ca (GoDaddy)** : ~$15-20/an (≈$1.50/mois)
- **Backups Vultr** : $1.50/mois (optionnel mais recommandé)
- **SSL Let's Encrypt** : Gratuit ✅
- **Total** : **≈$20-50/mois**

## 🛠️ Maintenance

### Commandes quotidiennes

```bash
# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps

# Redémarrer un service
docker-compose -f docker-compose.prod.yml restart frontend
```

### Mise à jour de l'application

```bash
cd /root/apps/le-grimoire
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Sauvegardes

Les sauvegardes automatiques sont configurées via cron (script dans [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md)).

Sauvegarde manuelle :
```bash
docker exec le-grimoire-mongodb mongodump --username=legrimoire --password=VOTRE_PASSWORD --authenticationDatabase=admin --db=legrimoire --out=/backup
docker cp le-grimoire-mongodb:/backup ./backup-$(date +%Y%m%d)
```

## 🐛 Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| Site ne charge pas | Vérifier `docker-compose ps` et `docker-compose logs` |
| DNS ne fonctionne pas | Vérifier `nslookup legrimoireonline.ca`, attendre propagation (24-48h) |
| Erreur SSL | Vérifier `certbot certificates`, renouveler avec `/root/renew-ssl.sh` |
| Conteneur ne démarre pas | Vérifier les logs avec `docker-compose logs [service]` |
| Erreur MongoDB | Vérifier l'espace disque `df -h`, redémarrer MongoDB |
| Performance lente | Vérifier `docker stats` et `htop`, upgrader le serveur |

Pour le dépannage détaillé, consultez [VULTR_DEPLOYMENT.md - Section Dépannage](./VULTR_DEPLOYMENT.md#dépannage).

## 📞 Support

### Documentation
- [Guide de démarrage](../getting-started/QUICKSTART.md)
- [Architecture](../architecture/OVERVIEW.md)
- [API Reference](../architecture/API_REFERENCE.md)
- [Guide de développement](../development/DEVELOPMENT.md)

### Communauté
- [GitHub Issues](https://github.com/sparck75/le-grimoire/issues) - Bugs et questions
- [GitHub Discussions](https://github.com/sparck75/le-grimoire/discussions) - Discussions générales

### Ressources externes
- [Vultr Documentation](https://www.vultr.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [GoDaddy Support](https://www.godaddy.com/help) - 1-800-581-0548 (Canada)

## 🎯 Prochaines étapes après le déploiement

1. **Sécurité**
   - [ ] Configurer un utilisateur non-root
   - [ ] Configurer fail2ban pour protection SSH
   - [ ] Activer les backups automatiques Vultr
   - [ ] Configurer Sentry pour le monitoring des erreurs

2. **Performance**
   - [ ] Configurer un CDN (Cloudflare)
   - [ ] Optimiser les images
   - [ ] Activer la compression Brotli
   - [ ] Configurer le caching Redis

3. **Monitoring**
   - [ ] Configurer Uptime monitoring (UptimeRobot, Pingdom)
   - [ ] Configurer des alertes (email, SMS)
   - [ ] Mettre en place des dashboards (Grafana)
   - [ ] Configurer des logs centralisés

4. **Features**
   - [ ] Configurer l'email (SMTP)
   - [ ] Ajouter Google Analytics
   - [ ] Configurer OAuth (Google, Apple)
   - [ ] Ajouter un système de newsletter

## ✅ Validation finale

Avant de considérer le déploiement terminé, assurez-vous que :

- ✅ https://legrimoireonline.ca charge correctement
- ✅ Certificat SSL valide (vérifier sur ssllabs.com)
- ✅ Tous les conteneurs sont actifs (`docker-compose ps`)
- ✅ Les logs ne montrent pas d'erreurs critiques
- ✅ Ingrédients OpenFoodFacts importés (5942 items)
- ✅ Sauvegardes automatiques configurées
- ✅ Renouvellement SSL automatique configuré
- ✅ Monitoring de base en place
- ✅ Documentation de production à jour

## 📝 Notes importantes

### Sécurité
- **Ne committez JAMAIS** le fichier `.env` avec les vraies valeurs
- Changez **tous les mots de passe** par défaut
- Générez des **clés secrètes** uniques et sécurisées
- Activez les **backups automatiques**
- Mettez à jour **régulièrement** le système et Docker

### Performance
- Commencez avec un serveur **2 vCPU / 4 GB RAM**
- Monitorer les ressources avec `docker stats` et `htop`
- Upgrader si nécessaire vers un plan plus puissant
- Configurer un **CDN** (Cloudflare) pour améliorer les performances

### Coûts
- Le déploiement coûte environ **$20-25/mois** pour commencer
- Peut augmenter à **$48-72/mois** pour haute performance
- SSL est **gratuit** avec Let's Encrypt
- Sauvegardes Vultr : **$1.50/mois** (recommandé)

---

**Bon déploiement ! 🚀**

Pour toute question, consultez la documentation complète ou ouvrez une issue sur GitHub.
