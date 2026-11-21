# Boîte à outils AfriShop

## Ce que fait le projet

`afrishop.py` est une petite bibliothèque d'analyse des ventes du premier trimestre d'AfriShop (200 ventes, 20 produits). Elle charge les fichiers CSV, calcule des statistiques descriptives (moyenne, médiane, écart-type), agrège le chiffre d'affaires par pays, canal ou statut, classe les produits, implémente la recherche dichotomique et mesure les liens entre variables (covariance, corrélation, matrice de covariance, valeurs propres 2x2).
Elle n'utilise **que la bibliothèque standard de Python** (`csv`, `math`, `pathlib`) : ni NumPy, ni Pandas. Seuls les tests demandent `pytest`.

## Récupérer les données

Les données sont dans l'archive `afrishop_m01_data.zip`, fournie avec le Module 01. Décompressez-la **à la racine du projet**, de façon à obtenir `donnees_m01/` à côté de `afrishop.py` :

```
seminaire-afrishop/
├── donnees_m01/
│   ├── produits.csv
│   └── ventes.csv
└── afrishop.py
```

Le dossier `donnees_m01/` n'est pas versionné (il est exclu par le `.gitignore`). Les données sont régénérées à chaque promotion et sont distribuées avec le module : elles n'ont pas leur place dans l'historique du code.

## Lancer le projet

Depuis le dossier du projet :

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv venv-m01
source venv-m01/bin/activate        # Windows : venv-m01\Scripts\activate

# 2. Installer l'outil de test
pip install pytest

# 3. Afficher le résumé du trimestre
python afrishop.py

# 4. Lancer les tests
pytest -q

# 5. (facultatif) Lancer les contrôles fournis avec le séminaire
python controles.py
```

Le module peut aussi être importé (`import afrishop`) : dans ce cas, il n'affiche rien.

## Ce que produit le résumé

Exemple de sortie de `python afrishop.py` (les chiffres changent d'une promotion à l'autre) :

```
Produits au catalogue : 20
Nombre de ventes      : 200
Lignes orphelines     : 0
Chiffre d'affaires    : 56,947.81
Top 3 des pays :
  1. CI                   15,312.61
  2. SN                   12,880.59
  3. CM                   11,599.97
Taux d'annulation     : 7.5%
```

- **Produits au catalogue** : le nombre de lignes de `produits.csv`.
- **Nombre de ventes** : le nombre de lignes de `ventes.csv`.
- **Lignes orphelines** : les ventes dont le produit n'existe pas au catalogue. Si la valeur n'est pas 0, les données sont incohérentes.
- **Chiffre d'affaires** : la somme des montants de toutes les ventes, en EUR.
- **Top 3 des pays** : les trois pays qui ont le plus gros chiffre d'affaires, du premier au troisième.
- **Taux d'annulation** : la part des ventes au statut `annulee`.

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `afrishop.py` | la bibliothèque : chargement, statistiques, tri et recherche, covariance |
| `test_afrishop.py` | les tests, lancés par `pytest -q` |
| `controles.py` | les contrôles fournis avec le séminaire, lancés par `python controles.py` |
| `exploration.ipynb` | le carnet d'exploration, exercice par exercice |
