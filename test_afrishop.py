"""Tests du module afrishop — séminaire du Module 01, Partie 5.

À lancer depuis ce dossier, environnement activé :  pytest -q

Au départ, les quatre tests échouent : ils ne sont pas encore écrits. Remplacez
chaque `pytest.fail(...)` par une ou plusieurs assertions. Objectif : « 4 passed ».
Si un test échoue alors qu'il est juste, c'est la fonction qu'on corrige, pas le test.
"""

import pytest
from afrishop import (
    convertir_ventes_robuste,
    covariance,
    mediane,
    moyenne,
    recherche_dichotomique,
    variance,
)

TOLERANCE = 1e-9   # pour comparer des flottants : abs(a - b) < TOLERANCE, jamais ==


def test_mediane_longueur_impaire():
    assert mediane([3, 1, 2]) == 2
    assert mediane([7, 1, 5, 3, 9]) == 5


def test_mediane_longueur_paire():
    assert abs(mediane([4, 1, 3, 2]) - 2.5) < TOLERANCE
    assert abs(mediane([10, 20]) - 15) < TOLERANCE


def test_covariance_avec_elle_meme_egale_la_variance():
    xs = [2.5, 4.0, 7.25, 1.0, 9.5]
    assert abs(covariance(xs, xs) - variance(xs)) < TOLERANCE


def test_recherche_dichotomique_cible_absente():
    ids = ["P01", "P03", "P05", "P07"]
    assert recherche_dichotomique(ids, "P04") == -1   # au milieu
    assert recherche_dichotomique(ids, "P00") == -1   # avant le début
    assert recherche_dichotomique(ids, "P99") == -1   # après la fin
    assert recherche_dichotomique([], "P01") == -1    # liste vide


# ------------------------------------------------------ Pour aller plus loin

def test_moyenne_liste_vide_leve_valueerror():
    # Une moyenne de zéro valeur n'a pas de sens : on refuse explicitement
    # plutôt que de laisser passer un ZeroDivisionError peu parlant.
    with pytest.raises(ValueError):
        moyenne([])


def test_convertir_ventes_robuste_compte_les_rejets():
    ventes = [
        {"id_vente": "V1", "quantite": "2", "mois": "1", "montant": "10.5"},
        {"id_vente": "V2", "quantite": "1", "mois": "2", "montant": ""},     # vide
        {"id_vente": "V3", "quantite": "x", "mois": "3", "montant": "5.0"},  # illisible
        {"id_vente": "V4", "quantite": "3", "mois": "3", "montant": "7.25"},
    ]
    valides, rejetees = convertir_ventes_robuste(ventes)
    assert rejetees == 2
    assert [v["id_vente"] for v in valides] == ["V1", "V4"]
    assert valides[0]["quantite"] == 2 and isinstance(valides[0]["montant"], float)
