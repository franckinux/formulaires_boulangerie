#!/usr/bin/env python3

# license : GPL 3.0
# copyright : Franck Barbenoire (franck@barbenoi.re)

"""
Ce programme propose deux types de calculs en fonction d'une contrainte de
départ :
- poids total de la pâte imposé : je veux faire un pain de 1kg, quels poids de
  farine, eau et levain dois-je mettre en fonction des taux d'hydratation du
  levain, du taux d'hydratation de la pâte désiré et de la proportion de levain
  par rapport à la farine ?
- poids du levain imposé : je dispose de 200g de levain, quels poids de farine
  et d'eau dois-je mettre et quel sera le poids de la pâte en fonction des taux
  d'hydratation du levain, du taux d'hydratation de la pâte désiré et de la
  proportion de levain par rapport à la farine ?

"""

import argparse
import configparser
import os
import sys

# début des formules

taux_sel = 0.02


def calcul_eau_farine_sel(thp, thl, tlf, pfl):
    """Calcule le poids de l'eau et le poids de la farine en fonction :
        - du taux d'hydratation de la pâte
        - du taux d'hydratation du levain
        - du taux de levain par rapport à la farine
        - du poids de la farine contenue dans le levain
    """
    global taux_sel
    pf = pfl / tlf
    pe = ((1 / tlf + 1) * thp - thl) * pfl
    ps = (pf + pfl) * taux_sel
    return pf, pe, ps


def calcul_pate_imposee(ptp, thp, thl, tlf):
    """Calcule les poids de la farine, de l'eau et du levain
    >>> calcul_pate_imposee(920, 0.6, 1.0, 0.3)
    (442.3, 212.3, 265.4, 11.5)
    """
    pfl = (ptp * tlf) / (1 + tlf) / (1 + thp)
    pf, pe, ps = calcul_eau_farine_sel(thp, thl, tlf, pfl)
    pl = (1 + thl) * pfl
    return round(pf, 1), round(pe, 1), round(pl, 1), round(ps, 1)


def calcul_levain_impose(pl, thp, thl, tlf):
    """Calcule les poids de la farine, de l'eau et de la pâte
    >>> calcul_levain_impose(200, 0.6, 1.0, 0.25)
    (400.0, 200.0, 800.0, 10.0)
    """
    pfl = pl / (1 + thl)
    pf, pe, ps = calcul_eau_farine_sel(thp, thl, tlf, pfl)
    ptp = pl + pf + pe
    return round(pf, 1), round(pe, 1), round(ptp, 1), round(ps, 1)


def calcul_equivalence(ptf, pte, thl, tlf):
    """Calcule les poids de la farine, de l'eau et du levain
    >>> calcul_equivalence(500, 300, 0.7, 0.4)
    (429.3, 199.0, 171.7, 10.0)
    """
    global taux_sel
    pf = ptf / (1 + tlf / (1 + 1 / thl))
    pe = pte - ptf * tlf / (1 + (1 + tlf) * thl)
    pl = pf * tlf

    ps = ptf * taux_sel
    return round(pf, 1), round(pe, 1), round(pl, 1), round(ps, 1)

# fin des formules


def saisie_valeur(msg, percent=False):
    while True:
        try:
            v = input(msg)
            v = float(v)
            if percent:
                v /= 100
            return v
        except ValueError:
            continue
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)


def saisie_taux(pate=True, levain=True):
    """
    Saisie des différents taux :
        - taux d'hydratation de la pâte
        - taux d'hydratation du levain
        - taux de levain par rapport à la farine
    Conversion dans l'intervalle [0-1]
    """
    if pate:
        thp = saisie_valeur("Taux d'hydratation de la pâte (%) : ", percent=True)
    else:
        thp = None
    if levain:
        thl = saisie_valeur("Taux d'hydratation du levain (%) : ", percent=True)
    else:
        thl = None
    tlf = saisie_valeur("Taux de farine du levain par rapport à la farine (%) : ", percent=True)
    return thp, thl, tlf


def pate_imposee():
    ptp = saisie_valeur("Poids de la pâte à obtenir : ")

    thp, thl, tlf = saisie_taux()
    pf, pe, pl, ps = calcul_pate_imposee(ptp, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids du levain : %.1f" % pl)
        print("Poids du sel (%.1f%% du poids total de farine) : %.1f" % (taux_sel * 100, ps))


def levain_impose():
    pl = saisie_valeur("Poids du levain : ")

    thp, thl, tlf = saisie_taux()
    pf, pe, ptp, ps = calcul_levain_impose(pl, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids de la pâte : %.1f" % ptp)
        print("Poids du sel (%.1f%% du poids total de farine) : %.1f" % (taux_sel * 100, ps))


def equivalence():
    ptf = saisie_valeur("Poids de la farine : ")
    pte = saisie_valeur("Poids de l'eau : ")

    thp, thl, tlf = saisie_taux(pate=False)
    pf, pe, pl, ps = calcul_equivalence(ptf, pte, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids du levain : %.1f" % pl)
        print("Poids du sel (%.1f%% du poids total de farine) : %.1f" % (taux_sel * 100, ps))


def iteratif():
    ptp = saisie_valeur("Poids de la pâte à obtenir : ")

    thp, thl, tlf = saisie_taux()

    for i in range(0, 5, 1):
        pf, pe, pl, ps = calcul_pate_imposee(ptp, thp, thl, tlf)

        if pe < 0:
            print("\nIncompatibililté des taux d'hydratation")
            break
        else:
            print("\nPoids de farine : %.1f" % pf)
            print("Poids d'eau : %.1f" % pe)
            print("Poids du levain : %.1f" % pl)
            if i == 0:
                print("Poids du sel (%.1f%% du poids total de farine) : %.1f" % (taux_sel * 100, ps))
            print("=====================================================")

        ptp = pl
        thp = thl
        _, thl, tlf = saisie_taux(pate=False)


def main():
    try:
        choix = input("poids de la pâte / poids du levain / equivalence / itératif (p/l/e/i) : ")
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)

    if choix == 'p':
        pate_imposee()
    elif choix == 'l':
        levain_impose()
    elif choix == 'e':
        equivalence()
    elif choix == 'i':
        iteratif()


def lire_taux_sel():
    global taux_sel
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.abspath(__file__))
    module = os.path.splitext(os.path.basename(__file__))[0]
    try:
        config.read(os.path.join(path, "config.ini"))
        if "formules" in config:
            taux_sel = float(config[module].get("taux_sel", 0.02))
        else:
            sys.stderr.write("Erreur dans le fichier de configuration\n")
            sys.exit(1)
    except:
        sys.stderr.write("Fichier de configuration non trouvé\n")
        sys.exit(1)


lire_taux_sel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="calculs sur le pain au levain")
    parser.add_argument('-t', "--test", action="store_true", help="passer les tests")
    parser.add_argument('-p', "--pate", action="store_true", help="poids de la pâte imposé")
    parser.add_argument('-l', "--levain", action="store_true", help="poids du levain imposé")
    parser.add_argument('-e', "--equivalence", action="store_true", help="équivalence")
    parser.add_argument('-i', "--iteratif", action="store_true", help="iteratif")
    args = parser.parse_args()

    if args.test:
        import doctest
        doctest.testmod()
    elif args.levain:
        levain_impose()
    elif args.pate:
        pate_imposee()
    elif args.equivalence:
        equivalence()
    elif args.iteratif:
        iteratif()
    else:
        main()
