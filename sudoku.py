"""Solveur de Sudoku par retour sur trace (backtracking).

Pour aller plus loin — Séminaire Module 01.

Une grille est une liste de 9 listes de 9 entiers ; 0 désigne une case vide.
Le principe : on place un chiffre dans la première case vide, on vérifie
qu'il ne viole ni sa ligne, ni sa colonne, ni son carré 3x3, puis on
recommence récursivement. Si aucun chiffre ne convient, on revient en
arrière et on essaie le suivant.
"""

import time

Grille = list[list[int]]


def grille_depuis_texte(ligne: str) -> Grille:
    """Transforme 81 caractères en grille 9x9 ('0' ou '.' pour une case vide)."""
    caracteres = [c for c in ligne if not c.isspace()]
    if len(caracteres) != 81:
        raise ValueError(f"81 caractères attendus, {len(caracteres)} reçus")
    chiffres = []
    for c in caracteres:
        if c == ".":
            chiffres.append(0)
        elif c.isdigit():
            chiffres.append(int(c))
        else:
            raise ValueError(f"caractère invalide : {c!r}")
    return [chiffres[i * 9:(i + 1) * 9] for i in range(9)]


def carre(grille: Grille, i: int, j: int) -> list[int]:
    """Renvoie les neuf valeurs du carré 3x3 contenant la case (i, j)."""
    i0, j0 = 3 * (i // 3), 3 * (j // 3)
    return [grille[a][b] for a in range(i0, i0 + 3) for b in range(j0, j0 + 3)]


def possibles(grille: Grille, i: int, j: int) -> list[int]:
    """Renvoie les chiffres jouables en (i, j), dans l'ordre croissant."""
    ligne = set(grille[i])
    colonne = {grille[a][j] for a in range(9)}
    interdits = ligne | colonne | set(carre(grille, i, j))
    return [c for c in range(1, 10) if c not in interdits]


def prochaine_case_vide(grille: Grille) -> tuple[int, int] | None:
    """Renvoie (i, j) de la première case vide, ou None si la grille est pleine."""
    for i in range(9):
        for j in range(9):
            if grille[i][j] == 0:
                return i, j
    return None


def resoudre(grille: Grille) -> bool:
    """Résout la grille EN PLACE. Renvoie True si une solution existe.

    Cas de base : plus de case vide, la grille est résolue.
    Cas récursif : essayer chaque chiffre possible dans la première case
    vide ; si la suite échoue, effacer la case (retour arrière).
    """
    case = prochaine_case_vide(grille)
    if case is None:
        return True
    i, j = case
    for chiffre in possibles(grille, i, j):
        grille[i][j] = chiffre
        if resoudre(grille):
            return True
        grille[i][j] = 0
    return False


def est_valide(grille: Grille) -> bool:
    """Vérifie qu'une grille pleine respecte toutes les règles."""
    attendu = set(range(1, 10))
    lignes = all(set(l) == attendu for l in grille)
    colonnes = all({grille[i][j] for i in range(9)} == attendu for j in range(9))
    carres = all(set(carre(grille, i, j)) == attendu
                 for i in (0, 3, 6) for j in (0, 3, 6))
    return lignes and colonnes and carres


def afficher(grille: Grille) -> None:
    """Affiche la grille avec les séparations des carrés 3x3."""
    for i, ligne in enumerate(grille):
        if i in (3, 6):
            print("------+-------+------")
        morceaux = [" ".join(str(c) if c else "." for c in ligne[k:k + 3])
                    for k in (0, 3, 6)]
        print(" | ".join(morceaux))


# Une grille facile et une grille réputée difficile pour le backtracking naïf
# (« Arto Inkala », 2012).
FACILE = ("530070000600195000098000060800060003400803001"
          "700020006060000280000419005000080079")
DIFFICILE = ("800000000003600000070090200050007000000045700"
             "000100030001000068008500010090000400")


if __name__ == "__main__":
    for nom, texte in (("facile", FACILE), ("difficile", DIFFICILE)):
        grille = grille_depuis_texte(texte)
        print(f"Grille {nom} :")
        afficher(grille)
        debut = time.perf_counter()
        ok = resoudre(grille)
        duree = time.perf_counter() - debut
        print(f"\nSolution ({duree * 1000:.1f} ms, valide : {ok and est_valide(grille)}) :")
        afficher(grille)
        print()
