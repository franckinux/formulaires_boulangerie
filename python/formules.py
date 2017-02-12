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


def saisie_taux(pate=True):
    """
    Saisie des différents taux :
        - taux d'hydratation de la pâte
        - taux d'hydratation du levain
        - taux de levain par rapport à la farine
    Conversion dans l'intervalle [0-1]
    """
    if pate:
        thp = input("Taux d'hydratation de la pâte (%) : ")
        thp = float(thp) / 100
    else:
        thp = None
    thl = input("Taux d'hydratation du levain (%) : ")
    thl = float(thl) / 100
    tlf = input("Taux de farine du levain par rapport à la farine (%) : ")
    tlf = float(tlf) / 100
    return thp, thl, tlf


def pate_imposee():
    ptp = input("Poids de la pâte à obtenir : ")
    ptp = float(ptp)

    thp, thl, tlf = saisie_taux()
    pf, pe, pl, ps = calcul_pate_imposee(ptp, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids du levain : %.1f" % pl)
        print("Poids du sel (2%% du poids total de farine) : %.1f" % ps)


def levain_impose():
    pl = input("Poids du levain : ")
    pl = float(pl)

    thp, thl, tlf = saisie_taux()
    pf, pe, ptp, ps = calcul_levain_impose(pl, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids de la pâte : %.1f" % ptp)
        print("Poids du sel (2%% du poids total de farine) : %.1f" % ps)


def equivalence():
    ptf = input("Poids de la farine : ")
    ptf = float(ptf)
    pte = input("Poids de l'eau : ")
    pte = float(pte)

    thp, thl, tlf = saisie_taux(pate=False)
    pf, pe, pl, ps = calcul_equivalence(ptf, pte, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids du levain : %.1f" % pl)
        print("Poids du sel (2%% du poids total de farine) : %.1f" % ps)


def main():
    choix = input("Poids total / poids du levain / equivalence (t/l/e) : ")
    if choix == 't':
        pate_imposee()
    elif choix == 'l':
        levain_impose()
    elif choix == 'e':
        equivalence()


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
    else:
        main()
