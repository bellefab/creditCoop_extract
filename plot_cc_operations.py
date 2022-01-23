#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import json
import getopt
from datetime import datetime
debug = False


def price_to_float(price_str):
    price_str = price_str.replace(',', '.')
    price_str = price_str.replace(' ', '')
    price_f = float(price_str)
    return price_f


def print_debug(s):
    if debug:
        print(s)
    else:
        pass


def usage():
    print(" CLI programm to plot Credit Cooperatif Bank data extracted from PDF.\n \
    Extraction has been writen in JSON file by program  extract-cc-pdf.py.\n \
     Usage : $ plot-cc-operations -i <inputfile>\n \
     where inputfile is a JSON file or \n \
     $ plot-cc-operations -f <files> \n \
     where files contains paths of input files in JSON \n \
     -d/--debug : print debug info \n \
     -h/--help : print this message \n \
     ")


def build_timerange(inputfile):
    with open(inputfile) as json_file:
        d = json.load(json_file)
        d_ope = d['operations']
        start_time = d_ope[0]['date']
        end_time = d_ope[len(d_ope)-1]['date']
        return datetime.strptime(start_time, "%d/%m"), datetime.strptime(end_time, "%d/%m")


def build_timeline(inputfile, ):
    with open(inputfile) as json_file:
        d = json.load(json_file)
        d_ope = d['operations']
        ope_timeline = []
        for elt in d_ope:
            # transform date in abs
            date = elt['date']
            ope_timeline.append(datetime.strptime(date, "%d/%m"))
        return ope_timeline


def build_montant_list(inputfile):
    with open(inputfile) as json_file:
        # TODO check that is a file, we can open, that is a JSON with
        # right definitions
        d = json.load(json_file)
        print_debug(d)
        # get soldes
        soldes = d['solde']

        # get the list of montant
        d_ope = d['operations']
        # d_ope is an array of bank operations
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
        print_debug(soldes)
        next = price_to_float(next)
        m_all.append(next)
        return montant_list, m_all


if __name__ == "__main__":
    inputfile = ""
    files = ""
    montant_list = []
    m_all = []
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                 "dhi:f:",
                                 ["debug", "help", "ifile=", "files="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-f", "--files"):
            files = arg
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    if args or len(opts) > 2:
        usage()
        sys.exit()
    if files != "":
        if inputfile != "":
            usage()
            sys.exit()
    elif inputfile == "":
        usage()
        sys.exit()

    if files != "":
        # Treat all lines to build globals montant_list and m_all
        ope_timeline = []
        montant_timeline = []
        # loop on files path contained in Files
        with open(files, 'r') as f:
            inputfile = ""
            for idx, line in enumerate(f):
                clean_line = line.strip()
                print_debug("--"+clean_line+"--")
                if clean_line != "":
                    inputfile = clean_line
                    start_time, end_time = build_timerange(inputfile)
                    montant_timeline.append(start_time)
                    ope_timeline += build_timeline(inputfile)
                    montant_timeline += build_timeline(inputfile)
                    montant_timeline.append(end_time)
                    m1, m1_all = build_montant_list(inputfile)
                    montant_list = montant_list + m1
                    m_all = m_all + m1_all
    else:
        start_time, end_time = build_timerange(inputfile)
        ope_timeline = build_timeline(inputfile)
        montant_list, m_all = build_montant_list(inputfile)
        montant_timeline = [start_time]
        montant_timeline += ope_timeline
        montant_timeline.append(end_time)
    plt.plot(ope_timeline, montant_list)
    plt.ylabel('Montant en euros')
    plt.show()

    print_debug(m_all)
    plt.plot(montant_timeline, m_all)
    plt.ylabel('Montant en euros')
    plt.show()
