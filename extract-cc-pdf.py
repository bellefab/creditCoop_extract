#!/usr/bin/env python3

import json
import sys
import getopt
import camelot


# Fields are :  date, message, credit, montant
class Mouvement:
    """
    Class representing an account mouvement.

    fileds are :
    - date
    - message : operations details
    - credit : Boolean, Tru if montant is a credit False if it is a debit
    - montant
    """
    def __init__(self):
        pass

    def __repr__(self):
        return ("date=%s montant=%s message=%s" % (self.date, self.montant, self.message))
        # str("date=%s montant=%s" % (self.date, self.montant))


def serialize_objects(obj):
    if isinstance(obj, Mouvement):
        return {
            'date': obj.date,
            'montant': obj.montant,
            'credit': obj.credit,
            'message': obj.message
        }
    raise TypeError(str(obj) + ' is not JSON serializable')


def check_soldes(prec, nouv, mvnt_list):
    prec = prec.replace(' ', '')
    prec = prec.replace(',', '.')
    prec_num = float(prec)
    current = prec_num
    for elt in mvnt_list:
        m = elt.montant
        m = m.replace(',', '.')
        m = m.replace(' ', '')
        if elt.credit:
            current = current + float(m)
        else:
            current = current - float(m)
    print("Check says old=%s new=%s, computed=%f" % (prec, nouv, current))


def print_debug1(tables):
    """

    """
    # number of tables extracted
    print("Total tables extracted:", tables.n)

    # print the  tables as Pandas DataFrame
    for i in range(tables.n):
        print(tables[i].df)
    print("---------------------------------\n\n")

    # let's say we ignore first and last tables
    #
    if tables.n <= 1:
        print("Error, only %d table detected\n" % (tables.n))

    for i in range(1, tables.n-1):
        print(tables[i].df)

    print("---------------------------------\n\n")


def treat_tables_ccFormat(tables):
    """
    # Prendre 1 table, avancer jusqu'a ligne où :
    # - col0 contient 'Date'
    # - col1 contient 'Détail des opérations ...'
    #
    # voir quelle num de col est "débit"
    # voir quel numéro de col est "crédit"

    # Ensuite pour chaque ligne si :
    #  col1 contient "SOLDE PRECEDENT ..." -> enregistrer date et solde précédent
    #  col1 contient  "NOUVEAU SOLDE ..." ->  enregistrer date et solde
    # sinon si col0 a une date, alors déterminer ligneN, la ligne de la prochaine date
    #  creer un Mouvement (date, detal , credit/debit, montant)
    # avec details pouvant être pris sur pls lignes.
    """

    mvnt_list = []  # liste vide
    solde_precedent = 0
    solde_nouveau = 0
    nb_mvnt = 0

    for i in range(1, tables.n-1):
        td = tables[i].df
        rows_nb = td.shape[0]
        cols_nb = td.shape[1]
        in_table = False
        message_multLine = False
        in_ope = False
        # for all lines
        for row in range(rows_nb):
            if td.iat[row, 0] == "Date" and \
             ("Détail des opérations" in td.iat[row, 1]):
                # TODO use regexp for 'Détail des opérations', should be better .. (?)
                # Find col for credit and for debit
                for col in range (2, cols_nb):
                    if "Crédit" in td.iat[row, col]:
                        credit_col = col
                    if "Débit" in td.iat[row, col]:
                        debit_col = col
                print("Crédit at %d Débit at %d \n" % (credit_col, debit_col))
                in_table = True
            elif not in_table:
                continue
            elif td.iat[row, 0] == "" and \
              ("SOLDE PRECEDENT" in td.iat[row, 1]):
                print("SOLDE PRECEDENT FOUND\n")
                in_ope = False
                if td.iat[row, credit_col] != "":
                    solde_precedent = td.iat[row, credit_col]
                else:
                    solde_precedent = td.iat[row, debit_col]
                # TODO
            elif td.iat[row, 0] == "" and \
             ("NOUVEAU SOLDE" in td.iat[row, 1]):
                print("NOUVEAU SOLDE FOUND\n")
                in_ope = False
                if td.iat[row, credit_col] != "":
                    solde_nouveau = td.iat[row, credit_col]
                else:
                    solde_nouveau = td.iat[row, debit_col]
                # TODO
            elif td.iat[row, 0] != "":
                # new mvnt
                in_ope = True
                mvnt = Mouvement()
                mvnt.date = td.iat[row, 0]
                if td.iat[row, credit_col] != "":
                    mvnt.credit = True
                    mvnt.montant = td.iat[row, credit_col]
                else:
                    mvnt.credit = False
                    mvnt.montant = td.iat[row, debit_col]
                # get operations details, and continue if following row has col0
                # empty (???)
                mvnt.message = td.iat[row, 1]
                if row < (rows_nb-1) and td.iat[row+1, 0] == "":
                    message_multLine = True
                mvnt_list.append(mvnt)
                nb_mvnt = nb_mvnt + 1
            elif td.iat[row, 0] == "" and \
              message_multLine and in_ope:
                # Set message !!!
                mvnt.message = mvnt.message + td.iat[row, 1]
                if row < (rows_nb-1) and td.iat[row+1, 0] != "":
                    message_multLine = False

    print("---------------------------------\n\n")
    print("------------nb_mvnt =%d---------------------\n\n" % (nb_mvnt))
    print(mvnt_list)

    check_soldes(solde_precedent, solde_nouveau, mvnt_list)

    solde = {}
    solde['solde_precedent_date'] = '0'
    solde['solde_precedent_montant'] = solde_precedent
    solde['solde_nouveau_montant'] = solde_nouveau

    return solde, mvnt_list


def write_file(solde, mvnt_list, type, outputfile):
    # TODO treat type other than json
    with open(outputfile, 'w') as f:
        data_all = {}
        data_all['solde'] = solde
        data_all['operations'] = mvnt_list
        json.dump(data_all, f, default=serialize_objects)


def usage():
    print(" CLI programm to extract Credit Cooperatif Bank data from PDF.\n \
    Extraction is writen in JSON.\n \
     Usage : $ extract-cc-pdf -i  <inputfile.pdf> -t <type> -o <outputfile.json>\n \
     Extract data from inputfile.pdf and write them in type (json) format \
     in outputfile.json")


if __name__ == "__main__":
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:t:", ["help", "ifile=", "ofile=", "type="])
    except getopt.GetoptError:
        print("Error in command line.")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        print(opt)
        print(arg)
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            # PDF file to extract tables from
            #file = "/home/fbelle-local/Téléchargements/RELEVES_0902258281_20191101.pdf"
            #file = "RELEVE.pdf"
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-t", "--type"):
            type = "json"  # TODO
    if args or len(opts) > 3:
        usage()
        sys.exit()
    if inputfile == "" or outputfile == "":
        usage()
        sys.exit()
    # TODO check that is a file, we can open, that is a PDF

    # extract all the tables in the PDF file
    tables = camelot.read_pdf(inputfile, pages='all', flavor='stream')

    print_debug1(tables)
    solde, mvnt_list = treat_tables_ccFormat(tables)
    write_file(solde, mvnt_list, type, outputfile)
