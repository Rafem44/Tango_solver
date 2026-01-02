# Guide d'utilisation de l'OCR Tango

## Installation des dépendances

```bash
pip install -r requirements.txt
```

Cela installera:
- `opencv-python` pour le traitement d'image
- `numpy` pour les calculs matriciels

## Utilisation

### 1. Résolution automatique depuis une image

La méthode la plus simple:

```bash
python solve_from_image.py votre_puzzle.png
```

Avec mode debug pour voir les détails:

```bash
python solve_from_image.py votre_puzzle.png --debug
```

### 2. Utilisation du module OCR seul

Pour tester seulement la reconnaissance:

```bash
python tango_ocr.py votre_puzzle.png
```

Cela affichera:
- La taille de grille détectée
- Les valeurs initiales trouvées (🟠 = 1, 🌙 = 0)
- Les contraintes détectées (= et ×)
- Une visualisation avec les détections superposées

## Formats d'images supportés

- PNG (recommandé)
- JPG/JPEG
- Tout format supporté par OpenCV

## Conseils pour de meilleurs résultats

1. **Screenshot clair**: Prenez un screenshot direct de l'application
2. **Contraste**: Assurez-vous que les couleurs sont bien visibles
3. **Cadrage**: Incluez toute la grille mais évitez trop d'espace vide autour
4. **Résolution**: Une résolution raisonnable (pas besoin de 4K, mais pas trop pixelisée)

## Fonctionnalités OCR actuelles

✅ **Détection de grille**: Trouve automatiquement la taille (6×6, 8×8, 10×10)
✅ **Reconnaissance de couleurs**: Détecte les cercles orange (1) et lunes bleues (0)
✅ **Architecture modulaire**: Prêt pour extensions futures

🔨 **En développement**: Détection des symboles = et × (nécessite template matching)

## Solvers disponibles

Après reconnaissance, plusieurs solvers sont disponibles:

- **Simple**: Propagation pure (V1 + contraintes)
- **V5**: Propagation avancée avec contraintes implicites (RECOMMANDÉ)

## Exemple complet

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Prendre un screenshot de votre puzzle Tango
# Sauvegarder comme "puzzle.png"

# 3. Résoudre automatiquement
python solve_from_image.py puzzle.png --debug

# 4. Le script affichera:
#    - État initial détecté
#    - Solution trouvée
#    - Validation (vérification des violations)
#    - Statistiques (temps, itérations, complétude)
```

## Dépannage

### "ModuleNotFoundError: No module named 'cv2'"
→ Installez les dépendances: `pip install -r requirements.txt`

### "Could not load image"
→ Vérifiez le chemin du fichier image
→ Vérifiez que l'image existe et est lisible

### "Detected grid size: 0×0"
→ L'OCR n'arrive pas à détecter la grille
→ Essayez avec une image plus claire ou mieux cadrée
→ Pour l'instant, utilisez la saisie manuelle

## Contact & Support

Pour tout problème ou suggestion d'amélioration, créez une issue sur le repo GitHub.

## Prochaines améliorations prévues

1. Détection robuste des contraintes = et × avec template matching
2. Support pour grilles non-carrées
3. Correction automatique de la perspective
4. Export de la solution en image
