"""Tests du solveur de Sudoku (bonus)."""

import pytest

from sudoku import (FACILE, carre, est_valide, grille_depuis_texte, possibles,
                    prochaine_case_vide, resoudre)


def test_grille_depuis_texte():
    grille = grille_depuis_texte(FACILE)
    assert len(grille) == 9 and all(len(l) == 9 for l in grille)
    assert grille[0][:3] == [5, 3, 0]


def test_grille_depuis_texte_longueur_invalide():
    with pytest.raises(ValueError):
        grille_depuis_texte("123")


def test_carre():
    grille = grille_depuis_texte(FACILE)
    assert carre(grille, 0, 0) == [5, 3, 0, 6, 0, 0, 0, 9, 8]
    assert carre(grille, 8, 8) == carre(grille, 6, 6)


def test_possibles():
    grille = grille_depuis_texte(FACILE)
    # Case (0, 2) : la ligne, la colonne et le carré excluent tout sauf 1, 2, 4.
    assert possibles(grille, 0, 2) == [1, 2, 4]


def test_prochaine_case_vide():
    grille = grille_depuis_texte(FACILE)
    assert prochaine_case_vide(grille) == (0, 2)
    resoudre(grille)
    assert prochaine_case_vide(grille) is None


def test_resoudre_facile():
    grille = grille_depuis_texte(FACILE)
    assert resoudre(grille)
    assert est_valide(grille)


def test_grille_impossible():
    # Ligne 0 : 1 à 8 placés, la case (0, 8) ne peut recevoir que 9 ;
    # or un 9 est déjà dans la colonne 8 (ligne 1) : aucune solution.
    texte = "123456780" + "000000009" + "0" * 63
    grille = grille_depuis_texte(texte)
    assert possibles(grille, 0, 8) == []
    assert not resoudre(grille)
