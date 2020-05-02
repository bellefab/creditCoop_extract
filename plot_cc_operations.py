#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import json



def price_to_float(price_str):
    price_str = price_str.replace(',', '.')
    price_str = price_str.replace(' ', '')
    price_f = float(price_str)
    return price_f


def usage():
    print(" CLI programm to plot Credit Cooperatif Bank data extractred from PDF.\n \
    Extraction has been writen in JSON file by program  extract-cc-pdf.py.\n \
     Usage : $ plot-cc-operations RELEVE.json\n \
     Extract data from RELEVE.pdf and write them in RELEVE.json")


if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) != 2:
        usage()
    else:
        file = sys.argv[1]
        with open(file) as json_file:
            # TODO check that is a file, we can open, that is a JSON with
            # right definitions
            d = json.load(json_file)
            print(d)
            # get soldes
            soldes = d['solde']

            # get the list of montant
            d_ope = d['operations']
            # dope is an array of bank operations
            montant_list = []
            for elt in d_ope:
                m = elt['montant']
                m_f = price_to_float(m)
                if not elt['credit']:
                    m_f = - m_f
                montant_list.append(m_f)

            m_all = []
            prec = soldes['solde_precedent_montant']
            prec = price_to_float(prec)
            m_all.append(prec)
            for m in montant_list:
                val = prec + m
                m_all.append(val)
                prec = val
            next = soldes['solde_nouveau_montant']
            next = price_to_float(next)
            m_all.append(next)

            print(montant_list)
            plt.plot(montant_list)
            plt.ylabel('some numbers')
            plt.show()

            print(m_all)
            plt.plot(m_all)
            plt.ylabel('some numbers')
            plt.show()
