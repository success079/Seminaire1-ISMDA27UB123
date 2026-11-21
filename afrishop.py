"""Boîte à outils d'analyse des ventes AfriShop — bibliothèque standard uniquement.

Séminaire du Module 01. Charger, résumer, trier, chercher et mesurer les liens
entre variables, sans NumPy ni Pandas.

CE FICHIER EST VOTRE POINT DE DÉPART. Les imports, la constante DOSSIER, ainsi
que la signature et la docstring de chaque fonction sont en place : les corps
sont à écrire. Chaque emplacement porte un TODO numéroté dans l'ordre des
exercices du sujet, avec son indice.

Une fonction encore vide lève NotImplementedError : ce n'est pas un bug, c'est
le signal qu'il reste un TODO. Remplacez la ligne `raise NotImplementedError(...)`
par votre code.

Pour savoir où vous en êtes :  python controles.py
"""

import csv
import math
from pathlib import Path

DOSSIER = Path("donnees_m01")


# --------------------------------------------------------------- Partie 1

def charger_csv(chemin: Path) -> list[dict]:
    """Charge un CSV en liste de dictionnaires, une entrée par ligne."""
    # TODO 1 : ouvrir le fichier en UTF-8 avec `with`, le lire avec
    #          csv.DictReader et renvoyer la LISTE de ses lignes.
    #          Piège : DictReader est un itérateur, il ne se parcourt qu'une fois.
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def convertir_ventes(ventes: list[dict]) -> list[dict]:
    """Convertit sur place les colonnes numériques des ventes."""
    # TODO 2 : convertir `quantite` et `mois` en int, `montant` en float,
    #          pour chaque vente, puis renvoyer la liste.
    #          Indice : modifier chaque dictionnaire dans une boucle suffit.
    for v in ventes:
        v["quantite"] = int(v["quantite"])
        v["mois"] = int(v["mois"])
        v["montant"] = float(v["montant"])
    return ventes


def convertir_ventes_robuste(ventes: list[dict]) -> tuple[list[dict], int]:
    """Convertit les ventes en écartant les lignes illisibles au lieu de s'arrêter.

    Une ligne dont `quantite`, `mois` ou `montant` est vide ou non numérique
    lève ValueError à la conversion : elle est alors rejetée et comptée.
    Renvoie (ventes_valides, nombre_de_lignes_rejetees).
    """
    valides: list[dict] = []
    rejetees = 0
    for v in ventes:
        try:
            convertie = {
                **v,
                "quantite": int(v["quantite"]),
                "mois": int(v["mois"]),
                "montant": float(v["montant"]),
            }
        except ValueError:
            rejetees += 1
            continue
        valides.append(convertie)
    return valides, rejetees


def convertir_produits(produits: list[dict]) -> list[dict]:
    """Convertit sur place les colonnes numériques des produits."""
    # TODO 3 : convertir `prix_unitaire` en float et `stock` en int,
    #          puis renvoyer la liste.
    for p in produits:
        p["prix_unitaire"] = float(p["prix_unitaire"])
        p["stock"] = int(p["stock"])
    return produits


def indexer(produits: list[dict]) -> dict[str, dict]:
    """Associe chaque id_produit à son dictionnaire produit."""
    # TODO 4 : renvoyer le dictionnaire `par_id` : id_produit -> produit complet.
    #          Indice : une compréhension de dictionnaire suffit.
    return {p["id_produit"]: p for p in produits}


def lignes_orphelines(ventes: list[dict], par_id: dict[str, dict]) -> int:
    """Compte les ventes dont l'id_produit n'existe pas au catalogue."""
    # TODO 5 : compter les ventes dont l'id_produit n'est PAS une clé de par_id.
    #          Sur les données du module, le résultat attendu est 0.
    return sum(1 for v in ventes if v["id_produit"] not in par_id)


# --------------------------------------------------------------- Partie 2

def moyenne(valeurs: list[float]) -> float:
    """Moyenne arithmétique. Lève ValueError sur une liste vide."""
    # TODO 6 : la somme des valeurs divisée par leur nombre.
    if not valeurs:
        raise ValueError("moyenne d'une liste vide : non définie")
    return sum(valeurs) / len(valeurs)


def mediane(valeurs: list[float]) -> float:
    """Valeur centrale : l'élément du milieu, ou la moyenne des deux du milieu."""
    # TODO 7 : trier une COPIE des valeurs, puis traiter les deux cas :
    #          nombre impair (l'élément du milieu) et nombre pair (la moyenne
    #          des deux du milieu).
    #          Indices : sorted(), len(), n // 2, n % 2.
    #          Piège : liste.sort() trierait la liste de l'appelant.
    tries = sorted(valeurs)
    n = len(tries)
    milieu = n // 2
    if n % 2 == 1:
        return tries[milieu]
    return (tries[milieu - 1] + tries[milieu]) / 2


def variance(valeurs: list[float]) -> float:
    """Variance d'échantillon, divisée par n-1 (estimateur sans biais)."""
    # TODO 8 : la somme des carrés des écarts à la moyenne, divisée par n-1.
    #          Réutilisez votre fonction moyenne.
    m = moyenne(valeurs)
    return sum((x - m) ** 2 for x in valeurs) / (len(valeurs) - 1)


def ecart_type(valeurs: list[float]) -> float:
    """Racine carrée de la variance d'échantillon."""
    # TODO 9 : à partir de votre fonction variance. Indice : math.sqrt.
    return math.sqrt(variance(valeurs))


def total_par(ventes: list[dict], cle: str) -> dict[str, float]:
    """Somme les montants en regroupant sur la colonne `cle` — un groupby manuel."""
    # TODO 10 : un dictionnaire qui associe chaque valeur de la colonne `cle`
    #           à la somme des montants des ventes concernées.
    #           Indice : resultat[k] = resultat.get(k, 0.0) + montant
    resultat: dict[str, float] = {}
    for v in ventes:
        k = v[cle]
        resultat[k] = resultat.get(k, 0.0) + v["montant"]
    return resultat


def taux_annulation(ventes: list[dict]) -> float:
    """Proportion de ventes au statut 'annulee', entre 0 et 1."""
    # TODO 11 : le nombre de ventes au statut "annulee", divisé par le nombre
    #           total de ventes. Une proportion (0.075), pas un pourcentage (7.5).
    annulees = sum(1 for v in ventes if v["statut"] == "annulee")
    return annulees / len(ventes)


# --------------------------------------------------------------- Partie 3

def ca_par_produit(ventes: list[dict]) -> dict[str, float]:
    """Chiffre d'affaires cumulé par identifiant de produit."""
    # TODO 12 : id_produit -> somme des montants de ses ventes.
    #           Une de vos fonctions de la Partie 2 fait déjà presque tout.
    return total_par(ventes, "id_produit")


def classer_produits(produits: list[dict], ca_produit: dict[str, float]) -> list[dict]:
    """Trie les produits par chiffre d'affaires décroissant."""
    # TODO 13 : renvoyer une NOUVELLE liste, triée par chiffre d'affaires
    #           décroissant. Un produit sans aucune vente compte pour 0.
    #           Indices : sorted(..., key=...), ca_produit.get(id, 0.0).
    return sorted(produits, key=lambda p: ca_produit.get(p["id_produit"], 0.0), reverse=True)


def recherche_dichotomique(identifiants: list[str], cible: str) -> int:
    """Indice de `cible` dans une liste TRIÉE, ou -1. Coût O(log n)."""
    # TODO 14 : réduire de moitié, à chaque tour, la zone où la cible peut être.
    #           Indices : gauche, droite = 0, len(identifiants) - 1
    #                     milieu = (gauche + droite) // 2
    #                     la boucle tourne tant que gauche <= droite
    #           Piège : sans le +1 / -1 en déplaçant les bornes, la boucle
    #                   ne s'arrête jamais sur une cible absente.
    gauche, droite = 0, len(identifiants) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        if identifiants[milieu] == cible:
            return milieu
        if identifiants[milieu] < cible:
            gauche = milieu + 1
        else:
            droite = milieu - 1
    return -1


def recherche_lineaire(identifiants: list[str], cible: str) -> int:
    """Indice de `cible`, ou -1. Coût O(n)."""
    # TODO 15 : parcourir la liste du début à la fin. Indice : enumerate().
    for i, ident in enumerate(identifiants):
        if ident == cible:
            return i
    return -1


# --------------------------------------------------------------- Partie 4

def covariance(xs: list[float], ys: list[float]) -> float:
    """Covariance d'échantillon, divisée par n-1."""
    # TODO 16 : la somme des produits des écarts à la moyenne, divisée par n-1.
    #           Indice : zip(xs, ys) parcourt les deux colonnes ensemble.
    mx, my = moyenne(xs), moyenne(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - 1)


def correlation(xs: list[float], ys: list[float]) -> float:
    """Coefficient de corrélation linéaire, entre -1 et 1."""
    # TODO 17 : la covariance, normalisée par le produit des écarts-types.
    return covariance(xs, ys) / (ecart_type(xs) * ecart_type(ys))


def matrice_covariance(colonnes: list[list[float]]) -> list[list[float]]:
    """Matrice symétrique de toutes les covariances deux à deux."""
    # TODO 18 : l'élément (i, j) est la covariance de la colonne i et de la
    #           colonne j. Indice : une double compréhension de liste suffit.
    return [[covariance(ci, cj) for cj in colonnes] for ci in colonnes]


def valeurs_propres_2x2(matrice: list[list[float]]) -> tuple[float, float]:
    """Valeurs propres d'une matrice 2x2, la plus grande en premier."""
    # TODO 19 : calculer la trace et le déterminant, puis résoudre
    #           lambda**2 - trace * lambda + det = 0.
    #           Renvoyer les deux racines, la plus grande en premier.
    (a, b), (c, d) = matrice
    trace = a + d
    det = a * d - b * c
    delta = trace ** 2 - 4 * det
    racine = math.sqrt(max(delta, 0.0))  # >= 0 pour une matrice symétrique
    return (trace + racine) / 2, (trace - racine) / 2


# --------------------------------------------------------------- Partie 5

def resume(dossier: Path = DOSSIER) -> None:
    """Charge les données et affiche le résumé du trimestre."""
    # TODO 20 : charger et convertir les deux fichiers, puis afficher le
    #           nombre de ventes, le chiffre d'affaires total, le top 3 des
    #           pays et le taux d'annulation.
    ventes = convertir_ventes(charger_csv(dossier / "ventes.csv"))
    produits = convertir_produits(charger_csv(dossier / "produits.csv"))
    par_id = indexer(produits)

    ca_total = sum(v["montant"] for v in ventes)
    par_pays = total_par(ventes, "pays")
    top3 = sorted(par_pays.items(), key=lambda kv: kv[1], reverse=True)[:3]

    print(f"Produits au catalogue : {len(produits)}")
    print(f"Nombre de ventes      : {len(ventes)}")
    print(f"Lignes orphelines     : {lignes_orphelines(ventes, par_id)}")
    print(f"Chiffre d'affaires    : {ca_total:,.2f}")
    print("Top 3 des pays :")
    for rang, (pays, montant) in enumerate(top3, start=1):
        print(f"  {rang}. {pays:<15s} {montant:>14,.2f}")
    print(f"Taux d'annulation     : {taux_annulation(ventes):.1%}")


# TODO 21 : ajouter ici le bloc qui appelle resume() quand le fichier est
#           LANCÉ (python afrishop.py), mais pas quand il est IMPORTÉ.

if __name__ == "__main__":
    resume()
