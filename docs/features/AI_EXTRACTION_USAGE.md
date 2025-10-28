# Guide d'utilisation de l'extraction IA de recettes

## Vue d'ensemble

Le Grimoire dispose désormais d'un système d'extraction de recettes alimenté par l'IA qui peut extraire intelligemment les ingrédients, instructions et métadonnées à partir d'images de recettes avec une précision de 90%+.

## Fonctionnalités

### Extraction automatique
- ✅ **Titre de la recette**
- ✅ **Description**
- ✅ **Nombre de portions**
- ✅ **Temps de préparation et de cuisson**
- ✅ **Difficulté** (Facile, Moyen, Difficile)
- ✅ **Type de cuisine** (Française, Italienne, etc.)
- ✅ **Catégorie** (Plat principal, Dessert, etc.)
- ✅ **Ingrédients structurés**
  - Nom de l'ingrédient
  - Quantité numérique
  - Unité de mesure
  - Notes de préparation complètes
- ✅ **Instructions étape par étape**
- ✅ **Outils nécessaires**
- ✅ **Notes et astuces**

### Score de confiance
Chaque extraction reçoit un score de confiance (0-1) basé sur la complétude des données extraites.

## Activation de la fonctionnalité

### Configuration requise

1. **Clé API OpenAI** : Vous devez obtenir une clé API OpenAI
   - Visitez https://platform.openai.com/api-keys
   - Créez un compte (5$ de crédit gratuit pour les nouveaux comptes)
   - Générez une clé API

2. **Variables d'environnement** :
   ```bash
   ENABLE_AI_EXTRACTION=true
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-votre-cle-api-ici
   OPENAI_MODEL=gpt-4o
   ```

3. **Redémarrer le backend** :
   ```bash
   docker-compose restart backend
   ```

## Utilisation

### Via l'interface web

1. Accédez à `/upload`
2. Sélectionnez ou prenez une photo d'une recette
3. Cliquez sur "Télécharger et extraire"
4. Le système détectera automatiquement si l'IA est disponible
5. Attendez l'extraction (généralement 3-5 secondes)
6. Vous serez redirigé vers le formulaire avec les données pré-remplies
7. Vérifiez et corrigez si nécessaire
8. Enregistrez la recette

### Via l'API

#### Vérifier le statut du service

```bash
curl http://localhost:8000/api/ai/status
```

Réponse :
```json
{
  "enabled": true,
  "provider": "openai",
  "openai_available": true,
  "fallback_enabled": true,
  "model": "gpt-4o"
}
```

#### Lister les fournisseurs disponibles

```bash
curl http://localhost:8000/api/ai/providers
```

Réponse :
```json
{
  "providers": {
    "tesseract": {
      "available": true,
      "type": "ocr",
      "cost": "free",
      "accuracy": "medium",
      "description": "Tesseract OCR - Free but lower accuracy"
    },
    "openai": {
      "available": true,
      "type": "ai",
      "cost": "paid",
      "accuracy": "high",
      "description": "GPT-4 Vision - High accuracy, paid service"
    }
  },
  "default": "openai",
  "ai_enabled": true,
  "fallback_enabled": true
}
```

#### Extraire une recette

```bash
curl -X POST http://localhost:8000/api/ai/extract \
  -F "file=@recette.jpg"
```

Ou avec un fournisseur spécifique :

```bash
curl -X POST http://localhost:8000/api/ai/extract?provider=openai \
  -F "file=@recette.jpg"
```

Réponse (exemple) :
```json
{
  "title": "Tomates vertes frites",
  "description": "Délicieuses tomates vertes panées et frites",
  "servings": 4,
  "prep_time": 15,
  "cook_time": 20,
  "difficulty": "Facile",
  "cuisine": "Américaine",
  "category": "Accompagnement",
  "ingredients": [
    {
      "ingredient_name": "Tomate verte",
      "quantity": 4,
      "unit": "unité",
      "preparation_notes": "4 grosses tomates vertes, tranchées"
    },
    {
      "ingredient_name": "Farine",
      "quantity": 1,
      "unit": "tasse",
      "preparation_notes": "1 tasse de farine tout usage"
    }
  ],
  "instructions": "1. Trancher les tomates vertes en rondelles de 1 cm...",
  "tools_needed": ["Poêle", "Spatule", "Assiette"],
  "notes": "Servir chaud avec une sauce ranch",
  "confidence_score": 0.92
}
```

## Conseils pour de meilleurs résultats

### Qualité de l'image

**Recommandé** :
- ✅ Éclairage naturel ou bon éclairage
- ✅ Photo droite (pas d'angle)
- ✅ Texte net et lisible
- ✅ Haute résolution (1080p minimum)
- ✅ Recettes imprimées

**Acceptable** :
- ⚠️ Recettes manuscrites (précision réduite à ~80%)
- ⚠️ Layouts complexes (multi-colonnes)
- ⚠️ Texte sur images

**Éviter** :
- ❌ Images floues
- ❌ Mauvais éclairage
- ❌ Angles extrêmes
- ❌ Texte très petit
- ❌ Polices décoratives difficiles à lire

### Types de recettes supportés

L'IA fonctionne particulièrement bien avec :
- Recettes de livres de cuisine
- Recettes imprimées
- Captures d'écran de sites web
- Recettes manuscrites lisibles
- Recettes en français et en anglais

## Coûts et limitations

### Coûts estimés (avec OpenAI GPT-4o)

- **Par recette** : ~0,03-0,05$ USD
- **1000 recettes/mois** : ~40-50$ USD
- **Crédit gratuit** : 5$ pour les nouveaux comptes (100-150 recettes)

### Optimisation des coûts

1. **Mode hybride** : Utilisez Tesseract pour les recettes simples
2. **Fallback automatique** : Si l'IA échoue, Tesseract prend le relais
3. **Compression d'images** : Les images sont automatiquement optimisées
4. **Désactivation temporaire** : `ENABLE_AI_EXTRACTION=false`

### Limites

- **Taille d'image** : 10 MB maximum
- **Formats** : JPG, PNG, WEBP
- **Taux de requêtes** : Selon les limites de l'API OpenAI
- **Quotas** : Selon votre plan OpenAI

## Dépannage

### "AI extraction is not enabled"

**Cause** : La fonctionnalité n'est pas activée

**Solution** :
1. Définir `ENABLE_AI_EXTRACTION=true` dans `.env`
2. Redémarrer le backend : `docker-compose restart backend`

### "OpenAI API key not configured"

**Cause** : La clé API n'est pas définie

**Solution** :
1. Obtenir une clé API sur https://platform.openai.com/api-keys
2. Définir `OPENAI_API_KEY=sk-...` dans `.env`
3. Redémarrer le backend

### L'extraction échoue ou retourne des données incomplètes

**Causes possibles** :
- Image de mauvaise qualité
- Texte illisible
- Format de recette non standard

**Solutions** :
1. Vérifier la qualité de l'image
2. Essayer avec une meilleure photo
3. Le système basculera automatiquement sur Tesseract si le fallback est activé
4. Vérifier le score de confiance retourné

### Coûts trop élevés

**Solutions** :
1. Utiliser le mode hybride (à venir)
2. Désactiver temporairement : `ENABLE_AI_EXTRACTION=false`
3. Utiliser Tesseract pour les recettes simples
4. Définir un budget mensuel dans votre compte OpenAI

## Mode de développement

Pour tester sans consommer de crédit API :

1. Utiliser Tesseract uniquement :
   ```bash
   ENABLE_AI_EXTRACTION=true
   AI_PROVIDER=tesseract
   ```

2. Ou désactiver complètement :
   ```bash
   ENABLE_AI_EXTRACTION=false
   ```

## Fallback automatique

Si l'extraction IA échoue et que `AI_FALLBACK_ENABLED=true` :

1. Le système essaie automatiquement Tesseract OCR
2. Les résultats seront moins structurés mais disponibles
3. Le score de confiance sera réduit (0.3)
4. L'utilisateur peut toujours corriger manuellement

## Comparaison des méthodes

| Méthode | Précision | Coût | Temps | Structure |
|---------|-----------|------|-------|-----------|
| **GPT-4 Vision** | 95%+ | ~$0.04 | 3-5s | Complète |
| **Tesseract** | 60-70% | Gratuit | 1-2s | Basique |
| **Hybride** | 85-95% | ~$0.02 | Variable | Variable |

## Feuille de route

### Fonctionnalités à venir
- [ ] Support de Google Gemini (moins cher)
- [ ] Routage intelligent (choisit automatiquement le meilleur fournisseur)
- [ ] Traitement par lots
- [ ] Support des recettes manuscrites amélioré
- [ ] Extraction à partir de vidéos
- [ ] Validation et nettoyage automatiques
- [ ] Tableau de bord d'analyse des coûts

## Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs du backend : `docker-compose logs backend`
2. Vérifiez le statut de l'API : `GET /api/ai/status`
3. Consultez la documentation OpenAI
4. Ouvrez une issue sur GitHub

## Ressources

- [Documentation OpenAI Vision](https://platform.openai.com/docs/guides/vision)
- [Tarification OpenAI](https://openai.com/pricing)
- [Analyse complète des options IA](../features/AI_RECIPE_EXTRACTION.md)
- [Guide d'implémentation](./AI_EXTRACTION_IMPLEMENTATION.md)

---

**Note importante** : Cette fonctionnalité nécessite une connexion Internet et envoie les images à un service externe (OpenAI). Assurez-vous que cela est acceptable pour votre cas d'usage. Pour les recettes confidentielles, utilisez le mode Tesseract uniquement ou considérez une solution locale (à venir).
