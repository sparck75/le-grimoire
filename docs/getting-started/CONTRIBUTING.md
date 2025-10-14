# Guide de contribution - Le Grimoire

Merci de votre intérêt pour contribuer à Le Grimoire ! Ce document vous guidera à travers le processus de contribution.

## Code de conduite

En participant à ce projet, vous acceptez de respecter notre code de conduite. Soyez respectueux, inclusif et professionnel dans toutes vos interactions.

## Comment contribuer

### Signaler des bugs

Si vous trouvez un bug :

1. Vérifiez qu'il n'a pas déjà été signalé dans les [issues](https://github.com/sparck75/le-grimoire/issues)
2. Créez une nouvelle issue avec :
   - Un titre clair et descriptif
   - Les étapes pour reproduire le bug
   - Le comportement attendu vs le comportement actuel
   - Captures d'écran si applicable
   - Votre environnement (OS, navigateur, version de Docker, etc.)

### Proposer des fonctionnalités

Pour proposer une nouvelle fonctionnalité :

1. Vérifiez qu'elle n'a pas déjà été proposée
2. Créez une issue avec le tag "enhancement"
3. Décrivez clairement :
   - Le problème que cette fonctionnalité résout
   - La solution proposée
   - Des alternatives envisagées
   - Des mockups ou exemples si applicable

### Soumettre des modifications

1. **Fork le projet**
   ```bash
   # Cliquez sur "Fork" sur GitHub
   ```

2. **Clonez votre fork**
   ```bash
   git clone https://github.com/votre-username/le-grimoire.git
   cd le-grimoire
   ```

3. **Créez une branche**
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   # ou
   git checkout -b fix/correction-du-bug
   ```

4. **Configurez l'environnement de développement**
   ```bash
   cp .env.example .env
   docker-compose up -d
   ```

5. **Faites vos modifications**
   - Suivez les conventions de code du projet
   - Commentez votre code si nécessaire
   - Testez vos modifications

6. **Committez vos changements**
   ```bash
   git add .
   git commit -m "feat: ajout de la fonctionnalité X"
   ```

   Utilisez les préfixes de commit conventionnels :
   - `feat:` pour une nouvelle fonctionnalité
   - `fix:` pour une correction de bug
   - `docs:` pour de la documentation
   - `style:` pour du formatage (pas de changement de code)
   - `refactor:` pour du refactoring
   - `test:` pour l'ajout de tests
   - `chore:` pour des tâches de maintenance

7. **Poussez vers votre fork**
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```

8. **Créez une Pull Request**
   - Allez sur le dépôt original sur GitHub
   - Cliquez sur "New Pull Request"
   - Sélectionnez votre branche
   - Décrivez vos modifications
   - Soumettez la PR

## Standards de code

### Python (Backend)

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez des type hints quand possible
- Documentez les fonctions avec des docstrings
- Limitez les lignes à 100 caractères

```python
def extract_text(image_path: str) -> str:
    """
    Extract text from image using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    # Implementation
    pass
```

### TypeScript (Frontend)

- Suivez les conventions Next.js et React
- Utilisez TypeScript strict
- Préférez les composants fonctionnels
- Utilisez des noms de fichiers en camelCase pour les composants

```typescript
interface RecipeProps {
  id: string;
  title: string;
}

export default function Recipe({ id, title }: RecipeProps) {
  // Implementation
}
```

### SQL

- Utilisez des noms de tables au pluriel en minuscules
- Utilisez snake_case pour les colonnes
- Ajoutez toujours des indexes pour les foreign keys
- Commentez les requêtes complexes

## Tests

### Backend

```bash
cd backend
pytest tests/
```

### Frontend

```bash
cd frontend
npm test
```

### Tests E2E

```bash
npm run test:e2e
```

## Structure du projet

Consultez [DEVELOPMENT.md](DEVELOPMENT.md) pour une vue détaillée de la structure du projet.

## Revue de code

Toutes les Pull Requests seront revues. Attendez-vous à :

- Des commentaires constructifs
- Des demandes de modifications
- Des tests automatisés qui doivent passer

## Questions ?

N'hésitez pas à :
- Ouvrir une issue avec le tag "question"
- Commenter sur une PR existante
- Contacter les mainteneurs

## Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence MIT que le projet.

Merci pour vos contributions ! 🎉
