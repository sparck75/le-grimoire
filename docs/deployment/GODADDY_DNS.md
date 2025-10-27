# Configuration DNS GoDaddy pour Le Grimoire

Ce guide vous explique comment configurer votre domaine `legrimoireonline.ca` sur GoDaddy pour qu'il pointe vers votre serveur Vultr.

## 📋 Prérequis

- Domaine `legrimoireonline.ca` enregistré sur GoDaddy
- Adresse IP publique de votre serveur Vultr (exemple: 45.76.123.45)
- Accès à votre compte GoDaddy

## 🌐 Étape 1 : Accéder à la gestion DNS

### 1.1 Se connecter à GoDaddy

1. Allez sur https://www.godaddy.com
2. Cliquez sur **"Sign In"** en haut à droite
3. Entrez vos identifiants GoDaddy
4. Cliquez sur **"Sign In"**

### 1.2 Accéder aux paramètres du domaine

1. Une fois connecté, cliquez sur votre nom/profil en haut à droite
2. Sélectionnez **"My Products"** dans le menu déroulant
3. Trouvez `legrimoireonline.ca` dans la liste de vos domaines
4. Cliquez sur le bouton **"DNS"** à côté du domaine
   - Ou cliquez sur les trois points (...) puis **"Manage DNS"**

Vous devriez maintenant voir la page de gestion DNS avec la liste de vos enregistrements DNS actuels.

## 🔧 Étape 2 : Configurer les enregistrements DNS

### 2.1 Supprimer les enregistrements existants (si nécessaire)

Si vous avez déjà des enregistrements A pour `@` (domaine racine) ou `www`, vous devez les supprimer ou les modifier :

1. Trouvez les enregistrements de type **"A"** avec le nom **"@"** ou **"www"**
2. Cliquez sur l'icône de **crayon** (éditer) ou sur **les trois points** puis **"Delete"** pour chaque enregistrement
3. Confirmez la suppression si demandé

### 2.2 Ajouter l'enregistrement A pour le domaine racine

Cet enregistrement fait pointer `legrimoireonline.ca` vers votre serveur.

1. Cliquez sur le bouton **"Add"** ou **"Add New Record"**
2. Configurez l'enregistrement comme suit :
   - **Type** : A
   - **Name** : @ (représente le domaine racine)
   - **Value** : L'adresse IP de votre serveur Vultr (exemple: 45.76.123.45)
   - **TTL** : 600 seconds (10 minutes) ou 1 hour (recommandé pour la production)
3. Cliquez sur **"Save"** ou **"Add Record"**

### 2.3 Ajouter l'enregistrement A pour www

Cet enregistrement fait pointer `www.legrimoireonline.ca` vers votre serveur.

1. Cliquez à nouveau sur **"Add"** ou **"Add New Record"**
2. Configurez l'enregistrement comme suit :
   - **Type** : A
   - **Name** : www
   - **Value** : L'adresse IP de votre serveur Vultr (même IP qu'à l'étape 2.2)
   - **TTL** : 600 seconds (10 minutes) ou 1 hour
3. Cliquez sur **"Save"** ou **"Add Record"**

### 2.4 Configuration finale

Votre configuration DNS devrait maintenant ressembler à ceci :

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 45.76.123.45 | 1 Hour |
| A | www | 45.76.123.45 | 1 Hour |

*(Remplacez 45.76.123.45 par l'IP réelle de votre serveur)*

### 2.5 Enregistrements optionnels

#### Enregistrement MX (pour les emails)

Si vous souhaitez recevoir des emails sur votre domaine (par exemple: contact@legrimoireonline.ca), vous devrez configurer des enregistrements MX. Cela nécessite un serveur de messagerie séparé.

**Option 1 : Utiliser Google Workspace ou Microsoft 365**
- Suivez les instructions de votre fournisseur de messagerie

**Option 2 : Utiliser un service de redirection d'emails**
- GoDaddy offre une redirection d'emails de base
- Allez dans "Email & Office" dans votre compte GoDaddy

#### Enregistrement TXT pour SPF (recommandé pour les emails)

Si vous envoyez des emails depuis votre serveur :

1. Cliquez sur **"Add"**
2. Configurez :
   - **Type** : TXT
   - **Name** : @
   - **Value** : `v=spf1 ip4:45.76.123.45 ~all` (remplacez par votre IP)
   - **TTL** : 1 hour
3. Cliquez sur **"Save"**

## ⏱️ Étape 3 : Attendre la propagation DNS

### 3.1 Temps de propagation

- **TTL initial** : Si vous venez de modifier les enregistrements, la propagation peut prendre de 10 minutes à 48 heures
- **En général** : La plupart des changements sont visibles en 30 minutes à 2 heures
- **Maximum** : Jusqu'à 48 heures dans les cas extrêmes

### 3.2 Vérifier la propagation DNS

#### Méthode 1 : Utiliser un outil en ligne

1. Allez sur https://www.whatsmydns.net/
2. Entrez `legrimoireonline.ca` dans le champ
3. Sélectionnez **"A"** dans le menu déroulant
4. Cliquez sur **"Search"**
5. Vérifiez que l'IP affichée correspond à celle de votre serveur Vultr

Répétez pour `www.legrimoireonline.ca`

#### Méthode 2 : Utiliser la ligne de commande

Sur **Linux/Mac** :

```bash
# Vérifier le domaine racine
dig legrimoireonline.ca +short

# Vérifier www
dig www.legrimoireonline.ca +short

# Ou avec nslookup
nslookup legrimoireonline.ca
nslookup www.legrimoireonline.ca
```

Sur **Windows** (PowerShell ou Command Prompt) :

```cmd
# Vérifier le domaine racine
nslookup legrimoireonline.ca

# Vérifier www
nslookup www.legrimoireonline.ca
```

La réponse devrait contenir l'adresse IP de votre serveur Vultr.

#### Méthode 3 : Utiliser votre navigateur

Essayez d'accéder à votre site (attendez au moins 30 minutes après la modification DNS) :

```
http://legrimoireonline.ca
http://www.legrimoireonline.ca
```

⚠️ **Note** : N'utilisez pas HTTPS pour l'instant, vous n'avez pas encore configuré SSL. Cela viendra après le déploiement (étape 5 du guide Vultr).

## 🔍 Étape 4 : Vérifications et tests

### 4.1 Vérifier depuis votre serveur

Connectez-vous à votre serveur Vultr :

```bash
ssh legrimoire@YOUR_SERVER_IP

# Vérifier que le domaine pointe vers ce serveur
curl -I http://legrimoireonline.ca

# Si nginx est déjà configuré, vous devriez voir une réponse HTTP
```

### 4.2 Tester la résolution DNS

```bash
# Vérifier la résolution DNS depuis le serveur
host legrimoireonline.ca
host www.legrimoireonline.ca

# Vérifier les enregistrements DNS
dig legrimoireonline.ca
dig www.legrimoireonline.ca
```

### 4.3 Vérifier avec ping

```bash
# Depuis votre ordinateur local
ping legrimoireonline.ca
ping www.legrimoireonline.ca

# Ctrl+C pour arrêter

# Vérifiez que l'IP affichée correspond à votre serveur Vultr
```

## 🚨 Problèmes courants et solutions

### Problème 1 : DNS ne se propage pas

**Symptômes** : Après plusieurs heures, le domaine ne pointe toujours pas vers votre serveur

**Solutions** :
1. Vérifiez que vous avez bien sauvegardé les modifications dans GoDaddy
2. Vérifiez que l'IP entrée est correcte
3. Videz le cache DNS de votre ordinateur :
   ```bash
   # Linux
   sudo systemd-resolve --flush-caches
   
   # Mac
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Windows (Command Prompt en administrateur)
   ipconfig /flushdns
   ```
4. Essayez depuis un autre réseau (données mobiles par exemple)
5. Attendez encore quelques heures (jusqu'à 48h maximum)

### Problème 2 : Le domaine affiche un contenu incorrect

**Symptômes** : Le domaine charge mais affiche une page de parking GoDaddy ou autre contenu

**Solutions** :
1. Vérifiez que nginx est bien démarré sur votre serveur :
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```
2. Vérifiez les logs nginx :
   ```bash
   docker compose -f docker-compose.prod.yml logs nginx
   ```
3. Assurez-vous que le pare-feu autorise le trafic sur les ports 80 et 443
4. Vérifiez la configuration nginx (voir VULTR_DEPLOYMENT.md)

### Problème 3 : www fonctionne mais pas le domaine racine (ou vice-versa)

**Symptômes** : `www.legrimoireonline.ca` fonctionne mais pas `legrimoireonline.ca`

**Solutions** :
1. Vérifiez que vous avez bien créé LES DEUX enregistrements A
2. Vérifiez que les deux enregistrements pointent vers la même IP
3. Attendez la propagation DNS (peut être différente pour chaque enregistrement)
4. Vérifiez la configuration nginx :
   ```bash
   docker compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/nginx.conf | grep server_name
   ```

### Problème 4 : ERR_SSL_VERSION_OR_CIPHER_MISMATCH

**Symptômes** : Message d'erreur SSL dans le navigateur

**Solutions** :
1. Assurez-vous d'avoir obtenu les certificats SSL (étape 5 du guide Vultr)
2. N'utilisez pas HTTPS avant d'avoir configuré SSL
3. Vérifiez que les certificats sont bien copiés dans nginx/ssl/
4. Redémarrez nginx après avoir ajouté les certificats

### Problème 5 : Connection Refused ou Timeout

**Symptômes** : Le navigateur affiche "Connection Refused" ou "Timed Out"

**Solutions** :
1. Vérifiez que votre serveur Vultr est bien démarré
2. Vérifiez que le pare-feu UFW autorise les ports 80 et 443 :
   ```bash
   sudo ufw status
   ```
3. Vérifiez que les conteneurs Docker sont bien démarrés :
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```
4. Vérifiez que nginx écoute bien sur les ports 80 et 443 :
   ```bash
   sudo netstat -tulpn | grep -E ':(80|443)'
   ```

## 📝 Configuration avancée (optionnel)

### Sous-domaines supplémentaires

Si vous souhaitez créer des sous-domaines (par exemple `api.legrimoireonline.ca` ou `admin.legrimoireonline.ca`) :

1. Dans GoDaddy DNS, cliquez sur **"Add"**
2. Configurez :
   - **Type** : A
   - **Name** : api (ou admin, ou autre)
   - **Value** : L'IP de votre serveur Vultr
   - **TTL** : 1 hour
3. Cliquez sur **"Save"**

Ensuite, mettez à jour votre configuration nginx pour gérer ce sous-domaine.

### Redirection de domaine

Si vous avez d'autres domaines qui doivent rediriger vers `legrimoireonline.ca` :

1. Dans GoDaddy, allez dans la gestion du domaine à rediriger
2. Allez dans **"Settings"** > **"Domain Forwarding"**
3. Configurez la redirection vers `legrimoireonline.ca`
4. Choisissez une redirection **301 (Permanent)**

### DNSSEC (optionnel)

Pour une sécurité accrue, vous pouvez activer DNSSEC :

1. Dans GoDaddy, allez dans les paramètres DNS
2. Cherchez l'option **"DNSSEC"**
3. Activez DNSSEC en suivant les instructions

⚠️ **Attention** : DNSSEC peut compliquer les modifications DNS. Activez-le uniquement si vous comprenez son fonctionnement.

## ✅ Checklist de configuration DNS

- [ ] Compte GoDaddy accessible
- [ ] Adresse IP du serveur Vultr notée
- [ ] Enregistrement A pour @ (domaine racine) créé
- [ ] Enregistrement A pour www créé
- [ ] Les deux enregistrements pointent vers la même IP
- [ ] Propagation DNS vérifiée avec whatsmydns.net
- [ ] Domaine accessible via HTTP (sans HTTPS pour l'instant)
- [ ] www.domaine et domaine tous deux accessibles
- [ ] Enregistrements optionnels (MX, TXT) configurés si nécessaire

## 🎯 Prochaines étapes

Une fois que votre DNS est configuré et propagé :

1. Retournez au [Guide de déploiement Vultr](./VULTR_DEPLOYMENT.md)
2. Continuez à l'**Étape 5 : Configuration SSL avec Let's Encrypt**
3. Configurez HTTPS pour sécuriser votre site

## 📚 Ressources supplémentaires

- [Documentation DNS GoDaddy](https://www.godaddy.com/help/manage-dns-records-680)
- [Guide Let's Encrypt](https://letsencrypt.org/getting-started/)
- [What's My DNS - Vérifier la propagation](https://www.whatsmydns.net/)
- [Guide Vultr DNS](https://www.vultr.com/docs/introduction-to-vultr-dns/)

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :

1. Consultez la section "Problèmes courants" ci-dessus
2. Vérifiez que tous les paramètres sont corrects
3. Attendez au moins 24 heures pour la propagation DNS
4. Contactez le support GoDaddy si le problème persiste
5. Ouvrez une issue sur le dépôt GitHub du projet

---

**Note importante** : N'oubliez pas de noter quelque part vos informations de configuration (adresse IP du serveur, nom d'utilisateur, etc.) dans un endroit sécurisé !
