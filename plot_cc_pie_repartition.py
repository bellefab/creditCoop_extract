#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import json
import getopt
debug = False
categories = []
total_input = 0


class category:
    name = ""
    selector = []
    color = ""
    montant_list = []
    total_amount = 0


def find_cat_update(ope):
    message = ope['message']
    # loop on all categories to find the good one
    for c in categories:
        if c.name != "Autre":
            for sel in c.selector:
                if message.startswith(sel):
                    c.total_amount += price_to_float(ope['montant'])
                    return
        else:
            print("Autre "+c.name+"--"+message+"--"+ope['montant'])
            c.total_amount += price_to_float(ope['montant'])

    # update the category


def sort_categories(inputfile):
    global total_input
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
        for ope in d_ope:
            if not ope['credit']:
                #print("ope-"+ope['message'])
                # check wich categories and append to it
                find_cat_update(ope)
            else:
                total_input += price_to_float(ope['montant'])


def price_to_float(price_str):
    price_str = price_str.replace(',', '.')
    price_str = price_str.replace(' ', '')
    price_f = float(price_str)
    return price_f


def display_value(pct, total_input):
    absolute = total_input/100*pct
    return "{:.1f}% {:.1f}$".format(pct, absolute)


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

    # Read json file for categories
    # Order each debit operation in one of categories
    # foreach debit ope (credit=false)
    # then check in cat if match
    # if YES add to list of this category
    categories = []
    with open("cat.json") as f_cat:
        d = json.load(f_cat)
        for c in d['categories']:
            cat = category()
            cat.name = c['name']
            cat.selector = c['selector']
            cat.color = c['color']
            cat.montant_list = []
            cat.total_amount = 0
            categories.append(cat)

    if files != "":
        # Treat all lines to build globals montant_list and m_all
        # loop on files path contained in Files
        with open(files, 'r') as f:
            inputfile = ""
            for idx, line in enumerate(f):
                clean_line = line.strip()
                #         print_debug("--"+clean_line+"--")
                if clean_line != "":
                    inputfile = clean_line
                    sort_categories(inputfile)
    else:
        sort_categories(inputfile)

    total_amount_all_cat = 0
    for c in categories:
        total_amount_all_cat += c.total_amount
        print(c.name+"--total="+str(c.total_amount))
    print("Dépenses totales ="+str(total_amount_all_cat))
    print("Entrées totales ="+str(total_input))
    if (total_input - total_amount_all_cat) < 0:
        print("DEBITEUR")
    else:
        cat = category()
        cat.name = "Reste"
        cat.selector = []
        cat.color = "none"
        cat.montant_list = []
        cat.total_amount = total_input - total_amount_all_cat
        categories.append(cat)

    # For Autre, regroup all elements with same message
    # Sort according value
    # display list
    fig, ax1 = plt.subplots()
    sizes = [c.total_amount for c in categories]
    labels = [c.name for c in categories]
    ax1.pie(sizes, labels=labels, autopct=lambda pct: display_value(pct, total_input))
    plt.show()
