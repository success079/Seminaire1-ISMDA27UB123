"""Contrôles automatiques du séminaire — à exécuter, pas à modifier.

Chaque contrôle appelle une fonction de afrishop.py et vérifie le « Résultat
attendu » du sujet, sur de petits exemples écrits à la main ou sur les données
du module. Les contrôles ne testent que ce qui ne change pas d'une promotion à
l'autre (200 ventes, 20 produits, 0 ligne orpheline...), jamais les chiffres
exacts d'une année : ceux-là, c'est à vous de les comparer au sujet.

Trois verdicts par fonction :
    OK         la fonction se comporte comme attendu
    À ÉCRIRE   la fonction lève encore NotImplementedError : un TODO reste à faire
    ÉCHEC      la fonction s'exécute, mais son résultat est faux : le message dit pourquoi

Depuis le notebook :  verifier("charger_csv")   ou   verifier("moyenne", "mediane")
Depuis le terminal :  python controles.py        (tous les contrôles, dans l'ordre du sujet)
"""

import importlib
import math
import statistics
import sys
import threading
from pathlib import Path

import afrishop

DOSSIER = Path("donnees_m01")
DELAI = 2.0  # secondes : au-delà, une recherche est considérée comme une boucle infinie


class Echec(Exception):
    """Un résultat faux, avec le message qui explique pourquoi."""


def _exiger(condition: bool, message: str) -> None:
    if not condition:
        raise Echec(message)


def _proche(a, b) -> bool:
    """Égalité de deux nombres à la précision flottante près (jamais == sur des flottants)."""
    return isinstance(a, (int, float)) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def _donnees() -> tuple[list[dict], list[dict]]:
    """Ventes et produits, chargés et convertis par VOS fonctions de la Partie 1."""
    ventes = afrishop.convertir_ventes(afrishop.charger_csv(DOSSIER / "ventes.csv"))
    produits = afrishop.convertir_produits(afrishop.charger_csv(DOSSIER / "produits.csv"))
    return ventes, produits


def _avec_delai(fonction, identifiants, cible):
    """Appelle une recherche, mais abandonne si elle ne se termine pas en DELAI secondes."""
    resultat = {}

    def appel():
        try:
            resultat["valeur"] = fonction(identifiants, cible)
        except BaseException as exc:  # l'erreur est relancée plus bas, hors du fil
            resultat["erreur"] = exc

    fil = threading.Thread(target=appel, daemon=True)
    fil.start()
    fil.join(DELAI)
    if fil.is_alive():
        raise Echec(f"la recherche de {cible!r} ne se termine pas après {DELAI:.0f} s : boucle infinie ? "
                    "Vérifiez le +1 / -1 en déplaçant les bornes. Dans le notebook, redémarrez ensuite le noyau.")
    if "erreur" in resultat:
        raise resultat["erreur"]
    return resultat["valeur"]


def _comparer(nom, fonction, reference, valeurs, conseil=""):
    """Compare une fonction statistique à celle du module statistics, sans modifier la liste."""
    copie = list(valeurs)
    obtenu = fonction(copie)
    _exiger(copie == list(valeurs),
            f"{nom} a modifié la liste reçue : {list(valeurs)} est devenue {copie}. Travaillez sur une copie (sorted).")
    attendu = reference(valeurs)
    _exiger(_proche(obtenu, attendu), f"{nom}({list(valeurs)}) donne {obtenu!r}, attendu {attendu!r}{conseil}")


# --------------------------------------------------------------- Partie 1

def _charger_csv():
    ventes = afrishop.charger_csv(DOSSIER / "ventes.csv")
    produits = afrishop.charger_csv(DOSSIER / "produits.csv")
    _exiger(isinstance(ventes, list),
            f"charger_csv doit renvoyer une liste, pas un {type(ventes).__name__} : avez-vous oublié list(...) ?")
    _exiger(len(ventes) == 200, f"ventes.csv donne {len(ventes)} lignes, attendu 200")
    _exiger(len(produits) == 20, f"produits.csv donne {len(produits)} lignes, attendu 20")
    _exiger(len(ventes[0]) == 8, f"une ligne de vente a {len(ventes[0])} clés, attendu 8")
    _exiger(all(isinstance(v, str) for v in ventes[0].values()),
            "avant conversion, toutes les valeurs d'une ligne doivent être des chaînes")


def _convertir_ventes():
    ventes = afrishop.convertir_ventes(afrishop.charger_csv(DOSSIER / "ventes.csv"))
    _exiger(isinstance(ventes, list) and len(ventes) == 200,
            "convertir_ventes doit renvoyer la liste des 200 ventes converties")
    for colonne, attendu in [("quantite", int), ("mois", int), ("montant", float)]:
        mauvais = [v[colonne] for v in ventes if type(v[colonne]) is not attendu]
        _exiger(not mauvais, f"`{colonne}` doit être un {attendu.__name__} : trouvé {mauvais[0]!r}" if mauvais else "")


def _convertir_produits():
    produits = afrishop.convertir_produits(afrishop.charger_csv(DOSSIER / "produits.csv"))
    _exiger(isinstance(produits, list) and len(produits) == 20,
            "convertir_produits doit renvoyer la liste des 20 produits convertis")
    for colonne, attendu in [("prix_unitaire", float), ("stock", int)]:
        mauvais = [p[colonne] for p in produits if type(p[colonne]) is not attendu]
        _exiger(not mauvais, f"`{colonne}` doit être un {attendu.__name__} : trouvé {mauvais[0]!r}" if mauvais else "")


def _indexer():
    _, produits = _donnees()
    par_id = afrishop.indexer(produits)
    _exiger(isinstance(par_id, dict), f"indexer doit renvoyer un dictionnaire, pas un {type(par_id).__name__}")
    _exiger(len(par_id) == 20, f"par_id a {len(par_id)} entrées, attendu 20")
    for produit in produits:
        cle = produit["id_produit"]
        _exiger(par_id.get(cle) == produit, f"par_id[{cle!r}] doit être le dictionnaire complet du produit {cle}")


def _lignes_orphelines():
    ventes, produits = _donnees()
    par_id = afrishop.indexer(produits)
    n = afrishop.lignes_orphelines(ventes, par_id)
    _exiger(n == 0, f"{n} lignes orphelines, attendu 0 : le chargement ou l'index est fautif")
    n = afrishop.lignes_orphelines(ventes + [{"id_produit": "P999"}], par_id)
    _exiger(n == 1, f"après ajout d'une vente fictive du produit inexistant P999, attendu 1 ligne orpheline, obtenu {n}")


# --------------------------------------------------------------- Partie 2

def _moyenne():
    for valeurs in ([1, 2, 3, 4], [10.0], [2.5, -1.5, 4.0]):
        _comparer("moyenne", afrishop.moyenne, statistics.mean, valeurs)


def _mediane():
    _comparer("mediane", afrishop.mediane, statistics.median, [3, 1, 2])
    _comparer("mediane", afrishop.mediane, statistics.median, [5])
    for valeurs in ([4, 1, 3, 2], [7, 7, 1, 9, 3, 2]):
        _comparer("mediane", afrishop.mediane, statistics.median, valeurs,
                  " (longueur paire : la moyenne des deux valeurs du milieu)")


def _variance():
    valeurs = [2, 4, 4, 4, 5, 5, 7, 9]
    obtenu = afrishop.variance(list(valeurs))
    _exiger(not _proche(obtenu, statistics.pvariance(valeurs)),
            f"variance({valeurs}) donne {obtenu!r} : c'est la division par n, le sujet demande n-1")
    _comparer("variance", afrishop.variance, statistics.variance, valeurs)
    _comparer("variance", afrishop.variance, statistics.variance, [1.5, 2.5])


def _ecart_type():
    for valeurs in ([2, 4, 4, 4, 5, 5, 7, 9], [1.5, 2.5, 10.0]):
        _comparer("ecart_type", afrishop.ecart_type, statistics.stdev, valeurs)


def _total_par():
    ventes, _ = _donnees()
    total = sum(v["montant"] for v in ventes)
    for cle, attendu in [("pays", 5), ("canal", 3), ("statut", 4)]:
        resultat = afrishop.total_par(ventes, cle)
        _exiger(isinstance(resultat, dict), f"total_par doit renvoyer un dictionnaire, pas un {type(resultat).__name__}")
        _exiger(len(resultat) == attendu, f"total_par(ventes, {cle!r}) a {len(resultat)} clés, attendu {attendu}")
        somme = sum(resultat.values())
        _exiger(math.isclose(somme, total, rel_tol=1e-9),
                f"la somme des totaux par {cle} ({somme:.2f}) n'égale pas le chiffre d'affaires total ({total:.2f})")


def _taux_annulation():
    for statuts, attendu in [(("annulee", "livree", "livree", "annulee"), 0.5),
                             (("annulee", "livree", "expediee", "en_attente"), 0.25)]:
        obtenu = afrishop.taux_annulation([{"statut": s} for s in statuts])
        conseil = " : une proportion entre 0 et 1, pas un pourcentage" if _proche(obtenu, attendu * 100) else ""
        _exiger(_proche(obtenu, attendu), f"sur les statuts {list(statuts)}, attendu {attendu}, obtenu {obtenu!r}{conseil}")
    ventes, _ = _donnees()
    taux = afrishop.taux_annulation(ventes)
    _exiger(0 < taux < 1, f"sur les ventes du module, le taux vaut {taux!r} : attendu une proportion entre 0 et 1")


# --------------------------------------------------------------- Partie 3

def _ca_par_produit():
    exemple = [{"id_produit": "A", "montant": 2.0}, {"id_produit": "B", "montant": 1.0},
               {"id_produit": "A", "montant": 3.0}]
    obtenu = afrishop.ca_par_produit(exemple)
    _exiger(obtenu == {"A": 5.0, "B": 1.0}, f"sur trois ventes A=2, B=1, A=3, attendu {{'A': 5.0, 'B': 1.0}}, obtenu {obtenu!r}")
    ventes, _ = _donnees()
    ca = afrishop.ca_par_produit(ventes)
    total = sum(v["montant"] for v in ventes)
    _exiger(math.isclose(sum(ca.values()), total, rel_tol=1e-9),
            "la somme des chiffres d'affaires par produit n'égale pas le chiffre d'affaires total")


def _classer_produits():
    produits = [{"id_produit": "A"}, {"id_produit": "B"}, {"id_produit": "C"}]
    try:
        obtenu = afrishop.classer_produits(produits, {"A": 1.0, "C": 5.0})
    except KeyError as exc:
        raise Echec(f"KeyError {exc} : un produit sans vente n'est pas une clé de ca_produit. "
                    "Il doit compter pour 0 : ca_produit.get(identifiant, 0.0)") from None
    ordre = [p["id_produit"] for p in obtenu]
    _exiger(ordre == ["C", "A", "B"],
            f"avec CA C=5, A=1 et B sans vente, attendu ['C', 'A', 'B'], obtenu {ordre} "
            "(ordre décroissant, un produit sans vente compte pour 0)")
    _exiger([p["id_produit"] for p in produits] == ["A", "B", "C"],
            "classer_produits a modifié la liste reçue : sorted() renvoie une nouvelle liste")


def _recherche(fonction):
    identifiants = [f"P{i:03d}" for i in range(1, 101)]
    for indice, cible in enumerate(identifiants):
        obtenu = _avec_delai(fonction, identifiants, cible)
        _exiger(obtenu == indice, f"la recherche de {cible!r} renvoie {obtenu!r}, attendu l'indice {indice}")
    for absente in ["P000", "P0505", "P999"]:
        obtenu = _avec_delai(fonction, identifiants, absente)
        _exiger(obtenu == -1, f"la recherche de {absente!r}, absente, renvoie {obtenu!r}, attendu -1")
    obtenu = _avec_delai(fonction, [], "P001")
    _exiger(obtenu == -1, f"sur une liste vide, la recherche renvoie {obtenu!r}, attendu -1")


def _recherche_dichotomique():
    _recherche(afrishop.recherche_dichotomique)


def _recherche_lineaire():
    _recherche(afrishop.recherche_lineaire)


# --------------------------------------------------------------- Partie 4

XS = [2.0, 4.0, 6.0, 8.0, 10.0]
YS = [1.0, 3.0, 2.0, 5.0, 4.0]
ZS = [9.0, 7.0, 8.0, 3.0, 1.0]


def _covariance():
    obtenu = afrishop.covariance(XS, YS)
    attendu = statistics.covariance(XS, YS)
    n = len(XS)
    _exiger(not _proche(obtenu, attendu * (n - 1) / n),
            f"covariance donne {obtenu!r} : c'est la division par n, le sujet demande n-1")
    _exiger(_proche(obtenu, attendu), f"covariance({XS}, {YS}) donne {obtenu!r}, attendu {attendu!r}")
    _exiger(_proche(afrishop.covariance(XS, XS), statistics.variance(XS)),
            "covariance(xs, xs) doit redonner la variance de xs")


def _correlation():
    obtenu = afrishop.correlation(XS, YS)
    attendu = statistics.correlation(XS, YS)
    _exiger(_proche(obtenu, attendu), f"correlation({XS}, {YS}) donne {obtenu!r}, attendu {attendu!r}")
    _exiger(_proche(afrishop.correlation(XS, XS), 1.0), "la corrélation d'une colonne avec elle-même doit valoir 1")
    _exiger(_proche(afrishop.correlation(XS, [-x for x in XS]), -1.0),
            "la corrélation d'une colonne avec son opposée doit valoir -1")


def _matrice_covariance():
    colonnes = [XS, YS, ZS]
    m = afrishop.matrice_covariance(colonnes)
    _exiger(len(m) == 3 and all(len(ligne) == 3 for ligne in m), "sur trois colonnes, attendu une matrice 3 x 3")
    for i in range(3):
        for j in range(3):
            attendu = statistics.covariance(colonnes[i], colonnes[j])
            _exiger(_proche(m[i][j], attendu), f"l'élément [{i}][{j}] vaut {m[i][j]!r}, attendu {attendu!r}")


def _valeurs_propres_2x2():
    for matrice, attendu in [([[2.0, 1.0], [1.0, 2.0]], (3.0, 1.0)),
                             ([[4.0, 0.0], [0.0, 9.0]], (9.0, 4.0)),
                             ([[5.0, 2.0], [2.0, 2.0]], (6.0, 1.0))]:
        obtenu = afrishop.valeurs_propres_2x2(matrice)
        _exiger(len(obtenu) == 2, f"attendu deux valeurs propres, obtenu {obtenu!r}")
        if _proche(obtenu[0], attendu[1]) and _proche(obtenu[1], attendu[0]):
            raise Echec(f"pour {matrice}, les valeurs sont justes mais dans le mauvais ordre : la plus grande d'abord")
        _exiger(_proche(obtenu[0], attendu[0]) and _proche(obtenu[1], attendu[1]),
                f"pour {matrice}, attendu {attendu}, obtenu {obtenu!r}")


CONTROLES = {
    "charger_csv": _charger_csv,
    "convertir_ventes": _convertir_ventes,
    "convertir_produits": _convertir_produits,
    "indexer": _indexer,
    "lignes_orphelines": _lignes_orphelines,
    "moyenne": _moyenne,
    "mediane": _mediane,
    "variance": _variance,
    "ecart_type": _ecart_type,
    "total_par": _total_par,
    "taux_annulation": _taux_annulation,
    "ca_par_produit": _ca_par_produit,
    "classer_produits": _classer_produits,
    "recherche_dichotomique": _recherche_dichotomique,
    "recherche_lineaire": _recherche_lineaire,
    "covariance": _covariance,
    "correlation": _correlation,
    "matrice_covariance": _matrice_covariance,
    "valeurs_propres_2x2": _valeurs_propres_2x2,
}


def verifier(*noms: str) -> None:
    """Lance les contrôles demandés, ou tous si aucun nom n'est donné, dans l'ordre du sujet."""
    try:
        importlib.reload(afrishop)  # relit afrishop.py : vos dernières modifications sont prises en compte
    except SyntaxError as exc:
        print(f"afrishop.py contient une erreur de syntaxe, ligne {exc.lineno} : {exc.msg}")
        return
    if not (DOSSIER / "ventes.csv").exists():
        print(f"Dossier {DOSSIER}/ introuvable depuis {Path.cwd()}. Décompressez afrishop_m01_data.zip "
              "dans le dossier seminaire-afrishop/, et lancez les contrôles depuis ce dossier.")
        return
    inconnus = [nom for nom in noms if nom not in CONTROLES]
    if inconnus:
        print(f"Contrôle inconnu : {', '.join(inconnus)}. Noms possibles : {', '.join(CONTROLES)}")
        return
    reussis = 0
    for nom in noms or CONTROLES:
        try:
            CONTROLES[nom]()
        except NotImplementedError as exc:
            print(f"À ÉCRIRE  {nom:24s} {exc}")
        except Echec as exc:
            print(f"ÉCHEC     {nom:24s} {exc}")
        except Exception as exc:
            print(f"ÉCHEC     {nom:24s} {type(exc).__name__} : {exc}")
        else:
            reussis += 1
            print(f"OK        {nom}")
    if not noms:
        print(f"\nBilan : {reussis} fonction(s) sur {len(CONTROLES)} au point.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows : sans cela, les accents font planter l'affichage
    verifier()
