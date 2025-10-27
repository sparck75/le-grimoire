# Configuration DNS GoDaddy pour Le Grimoire

Ce guide détaillé vous montre comment configurer votre domaine **legrimoireonline.ca** sur GoDaddy pour pointer vers votre serveur Vultr.

## 📋 Prérequis

- ✅ Compte GoDaddy avec le domaine **legrimoireonline.ca**
- ✅ Adresse IP de votre serveur Vultr (ex: `45.76.123.45`)
- ✅ Accès à votre compte GoDaddy

---

## 🔐 Connexion à GoDaddy

### Étape 1 : Accéder à votre compte

1. Allez sur **https://godaddy.com/**
2. Cliquez sur **Sign In** (en haut à droite)
3. Entrez vos identifiants GoDaddy
4. Cliquez sur **Sign In**

### Étape 2 : Accéder à la gestion des domaines

1. Une fois connecté, cliquez sur votre **nom d'utilisateur** en haut à droite
2. Sélectionnez **My Products** (Mes produits)
3. Vous verrez la liste de vos domaines et produits

---

## 🌐 Configuration des DNS

### Étape 3 : Accéder aux paramètres DNS

1. Trouvez **legrimoireonline.ca** dans la liste de vos domaines
2. Cliquez sur le bouton **DNS** (ou sur les **trois points** → **Manage DNS**)
3. Vous serez redirigé vers la page **DNS Management**

### Étape 4 : Voir les enregistrements actuels

Sur la page DNS Management, vous verrez plusieurs sections :
- **Records** (Enregistrements) - C'est ici que nous allons travailler
- **Nameservers** - Doit être sur "GoDaddy Nameservers" (par défaut)
- **DNSSEC** - Peut rester désactivé pour l'instant

### Étape 5 : Supprimer les enregistrements par défaut

GoDaddy ajoute généralement des enregistrements par défaut qui pointent vers leur page de parking. Nous devons les supprimer :

#### Enregistrements à supprimer :

1. **Enregistrement A avec nom "@"** qui pointe vers une IP GoDaddy (ex: `50.63.202.1`)
   - Cliquez sur l'icône **crayon** (Edit) ou **trois points** → **Delete**
   - Confirmez la suppression

2. **Enregistrement CNAME avec nom "www"** qui pointe vers `@` ou un domaine GoDaddy
   - Cliquez sur l'icône **crayon** ou **trois points** → **Delete**
   - Confirmez la suppression

3. **Enregistrement A avec nom "www"** (s'il existe)
   - Supprimez-le de la même manière

4. **Autres enregistrements A** qui ne sont pas nécessaires
   - Si vous voyez des enregistrements comme `_domainconnect`, vous pouvez les laisser
   - Supprimez seulement les enregistrements A et CNAME pour "@" et "www"

⚠️ **IMPORTANT** : Ne supprimez PAS les enregistrements :
- NS (Nameserver)
- SOA (Start of Authority)
- MX (Mail Exchange) - sauf si vous n'utilisez pas d'email
- TXT (comme SPF, DKIM) - laissez-les si vous utilisez l'email

### Étape 6 : Ajouter le nouvel enregistrement A pour le domaine principal

1. Cliquez sur le bouton **Add** (Ajouter) ou **Add New Record**
2. Remplissez les champs suivants :

**Configuration de l'enregistrement A principal :**

| Champ | Valeur | Exemple |
|-------|--------|---------|
| **Type** | Sélectionnez **A** dans le menu déroulant | A |
| **Name** (Nom) | Entrez **@** (représente legrimoireonline.ca) | @ |
| **Value** (Valeur) | Entrez l'adresse IP de votre serveur Vultr | `45.76.123.45` |
| **TTL** | Sélectionnez **Custom** puis entrez **600** (ou laissez **1 hour**) | 600 seconds |

3. Cliquez sur **Save** ou **Add Record**

✅ Cet enregistrement fera pointer **legrimoireonline.ca** vers votre serveur Vultr.

### Étape 7 : Ajouter l'enregistrement A pour www

1. Cliquez à nouveau sur **Add** ou **Add New Record**
2. Remplissez les champs :

**Configuration de l'enregistrement A pour www :**

| Champ | Valeur | Exemple |
|-------|--------|---------|
| **Type** | Sélectionnez **A** | A |
| **Name** | Entrez **www** | www |
| **Value** | Entrez la même IP Vultr | `45.76.123.45` |
| **TTL** | **600 seconds** ou **1 hour** | 600 seconds |

3. Cliquez sur **Save**

✅ Cet enregistrement fera pointer **www.legrimoireonline.ca** vers votre serveur.

### Alternative : Utiliser un CNAME pour www (Méthode 2)

Au lieu de créer un enregistrement A pour "www", vous pouvez utiliser un CNAME :

**Configuration de l'enregistrement CNAME pour www :**

| Champ | Valeur | Exemple |
|-------|--------|---------|
| **Type** | Sélectionnez **CNAME** | CNAME |
| **Name** | Entrez **www** | www |
| **Value** | Entrez **legrimoireonline.ca** (avec le point final) | legrimoireonline.ca. |
| **TTL** | **1 hour** | 3600 seconds |

⚠️ **Note** : GoDaddy peut automatiquement ajouter le point final (`.`) ou vous demander de l'ajouter.

---

## 📊 Vérification de la configuration

### Configuration finale

Après avoir terminé, vos enregistrements DNS devraient ressembler à ceci :

#### Option 1 : Avec deux enregistrements A

```
Type    Name    Value               TTL         Actions
----    ----    -----               ---         -------
A       @       45.76.123.45        600         Edit | Delete
A       www     45.76.123.45        600         Edit | Delete
NS      @       ns51.domaincontrol.com   1 hour      -
NS      @       ns52.domaincontrol.com   1 hour      -
SOA     @       Primary nameserver...    1 hour      -
```

#### Option 2 : Avec A + CNAME

```
Type    Name    Value                   TTL         Actions
----    ----    -----                   ---         -------
A       @       45.76.123.45            600         Edit | Delete
CNAME   www     legrimoireonline.ca     1 hour      Edit | Delete
NS      @       ns51.domaincontrol.com  1 hour      -
NS      @       ns52.domaincontrol.com  1 hour      -
SOA     @       Primary nameserver...   1 hour      -
```

Les deux options fonctionnent. L'option 2 (CNAME) est légèrement plus flexible si vous changez d'IP plus tard.

---

## ⏱️ Propagation DNS

### Temps de propagation

Après avoir sauvegardé vos changements, la propagation DNS peut prendre :
- **Minimum** : 15-30 minutes
- **Typique** : 2-6 heures
- **Maximum** : 24-48 heures

La propagation dépend de :
- Votre TTL (Time To Live) - 600 secondes = 10 minutes
- Les serveurs DNS de votre FAI
- La mise en cache DNS globale

### Vérifier la propagation DNS

#### Méthode 1 : Depuis votre ordinateur (Windows)

```cmd
# Ouvrir l'Invite de commandes (CMD)
nslookup legrimoireonline.ca

# Résultat attendu :
Server:  UnKnown
Address:  192.168.1.1

Non-authoritative answer:
Name:    legrimoireonline.ca
Address: 45.76.123.45
```

#### Méthode 2 : Depuis votre ordinateur (Mac/Linux)

```bash
# Terminal
dig legrimoireonline.ca

# Résultat attendu :
;; ANSWER SECTION:
legrimoireonline.ca.    600    IN    A    45.76.123.45
```

#### Méthode 3 : Outils en ligne (RECOMMANDÉ)

Utilisez ces outils pour vérifier depuis plusieurs endroits dans le monde :

1. **DNS Checker** (Meilleur outil)
   - URL : https://dnschecker.org/
   - Entrez : `legrimoireonline.ca`
   - Type : `A`
   - Cliquez sur **Search**
   - Vous verrez les résultats de plusieurs pays

2. **What's My DNS**
   - URL : https://www.whatsmydns.net/
   - Entrez : `legrimoireonline.ca`
   - Type : `A`

3. **Google DNS**
   - URL : https://dns.google/
   - Query : `legrimoireonline.ca`
   - RR Type : `A`

#### Vérification complète

```bash
# Vérifier le domaine principal
nslookup legrimoireonline.ca

# Vérifier le sous-domaine www
nslookup www.legrimoireonline.ca

# Les deux devraient retourner votre IP Vultr : 45.76.123.45
```

---

## 🔧 Dépannage DNS

### Problème 1 : Le domaine pointe toujours vers GoDaddy parking page

**Cause** : Les anciens enregistrements DNS n'ont pas été supprimés

**Solution** :
1. Retournez sur la page DNS Management de GoDaddy
2. Vérifiez qu'il n'y a pas d'enregistrements A ou CNAME qui pointent vers GoDaddy
3. Supprimez-les
4. Attendez 10-30 minutes
5. Videz le cache DNS de votre ordinateur :
   ```cmd
   # Windows
   ipconfig /flushdns
   
   # Mac
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   ```

### Problème 2 : "DNS_PROBE_FINISHED_NXDOMAIN"

**Cause** : Le domaine n'est pas encore propagé ou mal configuré

**Solution** :
1. Vérifiez que les Nameservers sont sur **GoDaddy Nameservers** (pas Custom)
   - Sur la page DNS Management, section **Nameservers**
   - Doit afficher : `ns51.domaincontrol.com` et `ns52.domaincontrol.com`
2. Si vous avez changé de Nameservers, attendez 24-48h
3. Vérifiez avec `nslookup` ou `dig`

### Problème 3 : Le domaine principal fonctionne mais pas www

**Cause** : Enregistrement www manquant ou mal configuré

**Solution** :
1. Retournez sur DNS Management
2. Vérifiez l'enregistrement pour "www"
3. Assurez-vous que :
   - Type : A ou CNAME
   - Name : www
   - Value : Votre IP ou legrimoireonline.ca

### Problème 4 : Propagation lente

**Cause** : TTL élevé ou cache DNS

**Solution** :
1. Attendez - c'est normal
2. Testez avec `nslookup` ou les outils en ligne
3. Essayez depuis un autre réseau (4G/5G de votre téléphone)
4. Testez en navigation privée pour éviter le cache du navigateur

### Problème 5 : Le site fonctionne avec l'IP mais pas avec le domaine

**Cause** : DNS pas encore propagé ou mauvais enregistrement

**Solution** :
1. Vérifiez `nslookup legrimoireonline.ca` - doit retourner votre IP
2. Si non, vérifiez la configuration DNS sur GoDaddy
3. Attendez la propagation (15min - 48h)
4. Testez avec https://dnschecker.org/

---

## 📝 Notes importantes

### À propos du TTL

**TTL (Time To Live)** détermine combien de temps les serveurs DNS gardent vos enregistrements en cache :

- **600 seconds (10 minutes)** : Recommandé pendant la configuration initiale ou les changements
- **3600 seconds (1 hour)** : Bon compromis pour production
- **86400 seconds (24 hours)** : Pour les configurations stables qui ne changent jamais

💡 **Conseil** : Gardez un TTL bas (600s) pendant les premières 24h, puis augmentez à 3600s.

### À propos des Nameservers

GoDaddy utilise par défaut ses propres nameservers :
- `ns51.domaincontrol.com`
- `ns52.domaincontrol.com`

⚠️ **Ne changez pas les nameservers** sauf si vous utilisez Cloudflare ou un autre service DNS externe.

### Email avec votre domaine

Si vous voulez utiliser **email@legrimoireonline.ca** :

1. Ne supprimez pas les enregistrements MX
2. Configurez un service email comme :
   - **GoDaddy Email** (service payant)
   - **Google Workspace** (anciennement G Suite)
   - **Microsoft 365**
   - **Zoho Mail** (gratuit pour 5 utilisateurs)
   - **ProtonMail**

Chaque service vous donnera des enregistrements MX et TXT à ajouter dans GoDaddy DNS Management.

---

## ✅ Checklist de vérification

Avant de considérer la configuration DNS terminée, vérifiez :

- [ ] Enregistrement A pour "@" créé avec votre IP Vultr
- [ ] Enregistrement A ou CNAME pour "www" créé
- [ ] Anciens enregistrements GoDaddy supprimés
- [ ] Nameservers sur "GoDaddy Nameservers"
- [ ] `nslookup legrimoireonline.ca` retourne votre IP
- [ ] `nslookup www.legrimoireonline.ca` retourne votre IP
- [ ] https://dnschecker.org/ montre votre IP dans plusieurs pays
- [ ] Navigation vers http://legrimoireonline.ca fonctionne
- [ ] Navigation vers http://www.legrimoireonline.ca fonctionne

---

## 🎉 Configuration terminée !

Votre domaine **legrimoireonline.ca** est maintenant configuré pour pointer vers votre serveur Vultr !

### Prochaines étapes

1. **Attendez la propagation DNS** (15min - 48h)
2. **Testez l'accès HTTP** : http://legrimoireonline.ca
3. **Configurez SSL/TLS** avec Let's Encrypt (voir [VULTR_DEPLOYMENT.md](./VULTR_DEPLOYMENT.md))
4. **Testez l'accès HTTPS** : https://legrimoireonline.ca

---

## 📞 Support

### Ressources GoDaddy

- **Centre d'aide** : https://www.godaddy.com/help
- **Téléphone (Canada)** : 1-800-581-0548
- **Chat en direct** : Disponible sur godaddy.com après connexion

### Ressources Le Grimoire

- [Guide de déploiement Vultr complet](./VULTR_DEPLOYMENT.md)
- [Documentation complète](../README.md)
- [GitHub Issues](https://github.com/sparck75/le-grimoire/issues)

---

## 🔍 Captures d'écran de référence

### 1. Page "My Products"
Vous devriez voir votre domaine **legrimoireonline.ca** avec un bouton **DNS**.

### 2. Page "DNS Management"
Sections visibles :
- **Records** (avec bouton Add)
- **Nameservers** (doit être "GoDaddy Nameservers")
- **DNSSEC**

### 3. Formulaire "Add Record"
Champs :
- Type (dropdown)
- Name (texte)
- Value (texte)
- TTL (dropdown)
- Bouton Save

---

**Note** : Les interfaces GoDaddy peuvent légèrement varier selon la version. Si vous ne trouvez pas exactement les mêmes options, cherchez des termes similaires comme "DNS", "Records", "A Record", etc.
