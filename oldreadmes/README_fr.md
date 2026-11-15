# TP4 — Technique d'entrée de texte gestuelle

## Description

Implémentation d'un clavier gestuel de type *shape writing* (tracé de forme). L'utilisateur dessine un tracé continu sur le clavier en passant par les lettres du mot souhaité. Le système reconnaît le mot le plus probable grâce au rééchantillonnage du tracé et à l'algorithme **Dynamic Time Warping (DTW)**.

## Prérequis

- Python 3.x
- PyQt5
- Le fichier `mots.txt` (dictionnaire français, inclus dans le dépôt)
- Le fichier `layout.json` (disposition du clavier, inclus dans le dépôt)

## Lancement

```bash
python main.py
```

## Utilisation

- **Tracé gestuel** — maintenir le clic gauche enfoncé et glisser sur les lettres du mot souhaité, puis relâcher. Les recommandations apparaissent en haut du clavier.
- **Clic simple** — appuyer et relâcher sur une touche pour saisir une lettre directement.
- **Sélection d'un mot** — cliquer sur l'une des recommandations affichées pour l'insérer dans le champ de texte.

## Structure des fichiers

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée — lance l'éditeur de texte avec le clavier gestuel |
| `keyboard_widget.py` | Widget principal : affichage du clavier, gestion des événements souris, calcul des recommandations |
| `key.py` | Classe `Key` — représente une touche avec sa position et ses dimensions en pixels |
| `reconnaisseur.py` | Fonctions de rééchantillonnage du tracé (`resample`, `interpolate`) |
| `dtw.py` | Implémentation de l'algorithme Dynamic Time Warping |
| `dictionnaire.py` | Chargement du dictionnaire et pré-calcul des tracés idéaux par mot |
| `layout.json` | Disposition du clavier (positions, tailles des touches) |
| `mots.txt` | Dictionnaire de mots français utilisé pour la reconnaissance |

## Fonctionnement technique

### Rééchantillonnage

Le tracé brut de l'utilisateur est rééchantillonné à intervalle fixe `d` via `resample()` pour obtenir une séquence de points uniformément espacés. Cela rend la comparaison indépendante de la vitesse de saisie.

### Génération des tracés de référence

Au chargement, pour chaque mot du dictionnaire, un tracé idéal est généré en reliant les centres des touches correspondantes, puis rééchantillonné avec le même `d`. Ces tracés sont stockés dans `Dictionnaire` pour la comparaison.

### Reconnaissance par DTW

Le tracé utilisateur rééchantillonné est comparé à chaque tracé de référence via DTW. Les `nbReco` mots ayant la distance minimale sont proposés comme recommandations.

## Optimisations réalisées

### Filtrage par première lettre

Le dictionnaire est indexé par première lettre (`words_by_letter`). Lors de la reconnaissance, seuls les mots commençant par la même lettre que le début du tracé sont comparés — ce qui réduit drastiquement le nombre de comparaisons DTW.

### Pré-calcul des tracés de référence

Les tracés idéaux de tous les mots sont calculés **une seule fois au démarrage** et mis en cache dans les objets `Mot`. Sans cela, chaque tracé utilisateur déclencherait un recalcul complet pour tout le dictionnaire.

### Accès aux touches en O(1)

Un `key_map` (dictionnaire Python) indexe les touches par symbole, évitant de parcourir la liste complète des touches à chaque génération de tracé de référence.

### Calcul Parallèle d DTW en arrière-plan (QThread)

Le calcul DTW sur les candidats est délégué à un `DTWWorker` qui hérite de `QThread`. Le thread émet un signal `finished` une fois les recommandations prêtes, ce qui permet à l'interface de rester **responsive** pendant le calcul
— l'utilisateur peut continuer à interagir avec le clavier sans blocage.

### Lissage du tracé par courbes de Bézier

Le tracé affiché n'est pas dessiné segment par segment mais via des courbes de
Bézier quadratiques (`QPainterPath.quadTo`). Pour chaque paire de points
consécutifs, le point de contrôle est le point brut et la destination est leur
milieu — ce qui produit un tracé visuellement lisse et continu, sans angles
brusques.