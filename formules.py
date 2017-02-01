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


def saisie_taux():
    """
    Saisie des différents taux :
        - taux d'hydratation de la pâte
        - taux d'hydratation du levain
        - taux de levain par rapport à la farine
    Conversion dans l'intervalle [0-1]
    """
    thp = input("Taux d'hydratation de la pâte (%) : ")
    thp = float(thp) / 100
    thl = input("Taux d'hydratation du levain (%) : ")
    thl = float(thl) / 100
    tlf = input("Taux de farine du levain par rapport à la farine (%) : ")
    tlf = float(tlf) / 100
    return thp, thl, tlf


def calcul_eau_farine(thp, thl, tlf, pfl):
    """Calcule le poids de l'eau et le poids de la farine en fonction :
        - du taux d'hydratation de la pâte
        - du taux d'hydratation du levain
        - du taux de levain par rapport à la farine
        - du poids de la farine contenue dans le levain
    """
    pf = pfl / tlf
    pe = ((1 / tlf + 1) * thp - thl) * pfl
    return pf, pe


def calcul_eau_farine_levain(ptp, thp, thl, tlf):
    """Calcule les poids de la farine, de l'eau et du levain
    >>> calcul_eau_farine_levain(920, 0.6, 1.0, 0.3)
    (442.3, 212.3, 265.4, 11.5)
    """
    pfl = (ptp * tlf) / (1 + tlf) / (1 + thp)
    pf, pe = calcul_eau_farine(thp, thl, tlf, pfl)
    pl = (1 + thl) * pfl
    ps = (pf + pfl) * 0.02
    return round(pf, 1), round(pe, 1), round(pl, 1), round(ps, 1)


def pate():
    ptp = input("Poids de la pâte à obtenir : ")
    ptp = float(ptp)

    thp, thl, tlf = saisie_taux()
    pf, pe, pl, ps = calcul_eau_farine_levain(ptp, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids du levain : %.1f" % pl)
        print("Poids du sel (2%% du poids total de farine) : %.1f" % ps)


def calcul_eau_farine_pate(pl, thp, thl, tlf):
    """Calcule les poids de la farine, de l'eau et de la pâte
    >>> calcul_eau_farine_pate(200, 0.6, 1.0, 0.25)
    (400.0, 200.0, 800.0, 10.0)
    """
    pfl = pl / (1 + thl)
    pf, pe = calcul_eau_farine(thp, thl, tlf, pfl)
    ptp = pl + pf + pe
    ps = (pf + pfl) * 0.02
    return round(pf, 1), round(pe, 1), round(ptp, 1), round(ps, 1)


def levain():
    pl = input("Poids du levain : ")
    pl = float(pl)

    thp, thl, tlf = saisie_taux()
    pf, pe, ptp, ps = calcul_eau_farine_pate(pl, thp, thl, tlf)

    if pe < 0:
        print("\nIncompatibililté des taux d'hydratation")
    else:
        print("\nPoids de farine : %.1f" % pf)
        print("Poids d'eau : %.1f" % pe)
        print("Poids de la pâte : %.1f" % ptp)
        print("Poids du sel (2%% du poids total de farine) : %.1f" % ps)


def main():
    choix = input("Poids total ou poids du levain (t/l) : ")
    if choix == 't':
        pate()
    elif choix == 'l':
        levain()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="calculs sur le pain au levain")
    parser.add_argument('-t', "--test", action="store_true", help="passer les tests")
    parser.add_argument('-p', "--pate", action="store_true", help="poids de la pâte imposé")
    parser.add_argument('-l', "--levain", action="store_true", help="poids du levain imposé")
    args = parser.parse_args()

    if args.test:
        import doctest
        doctest.testmod()
    elif args.levain:
        levain()
    elif args.pate:
        pate()
    else:
        main()
