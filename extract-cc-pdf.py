#!/usr/bin/env python3

import json
import sys
import getopt
sys.path.insert(1, '../camelot')
import camelot

debug = False
# For CreditCooperatif releve since 06 2018
# use the following table_region.
# It allows to avoid to analyse Page Headers as tables.
# Coordinates have been obtained using ghostview viewer 'gv'.
cc_table_regions_062018 = "135,760,780,135"
cc_columns_sep_062018 = "170,430,480"

# For format of Credit Cooperatif relevés before 06 2018
# define regions to search for table, do not consider
# page header, in this format there is the same big page header
# on each page.
# Define columns or lago will not be able to split lines in columns
# and all rows will have a uniq value in first column.
cc_table_regions_before_062018 = "40,560,550,130"
cc_columns_sep_before_062018 = "80,260,350,430"

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
        return ("date=%s montant=%s message=%s" %
                (self.date, self.montant, self.message))


def print_debug(s):
    if debug:
        print(s)
    else:
        pass


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
    print_debug("Check says old=%s new=%s, computed=%f" %
                (prec, nouv, current))


def print_debug1(tables):
    """
    Very verbose print
    """
    # number of tables extracted
    print_debug("Total tables extracted: %d" % (tables.n))

    # print the  tables as Pandas DataFrame
    for i in range(tables.n):
        print_debug(tables[i].df)
    print_debug("---------------------------------\n\n")

    for i in range(tables.n):
        print_debug(tables[i].df)

    print_debug("---------------------------------\n\n")


def treat_tables_ccFormat(tables):
    """
    Prendre 1 table, avancer jusqu'a ligne où :
     - col0 contient 'Date'
     - col1 contient 'Détail des opérations ...'

     voir quelle num de col est "débit"
     voir quel numéro de col est "crédit"

     Ensuite pour chaque ligne si :
      col1 contient "SOLDE PRECEDENT .." -> enregistrer date et solde précédent
      col1 contient  "NOUVEAU SOLDE .." ->  enregistrer date et solde
     sinon si col0 a une date, alors déterminer ligneN, la ligne de
     la prochaine date creer un Mouvement (date, detal , credit/debit, montant)
     avec details pouvant être pris sur pls lignes.
    """

    mvnt_list = []  # liste vide
    solde_precedent = 0
    solde_nouveau = 0
    nb_mvnt = 0

    for i in range(tables.n):
        td = tables[i].df
        rows_nb = td.shape[0]
        cols_nb = td.shape[1]
        in_table = False
        message_multLine = False
        in_ope = False
        # Test if tables is to analyse
        # considered to analyse if exist row with col0 ==  "Date"
        #  and exists cols "Crédit","Débit"
        table_to_analyse = False
        for row in range(rows_nb):
            if td.iat[row, 0] == "Date" and \
             ("Détail des opérations" in td.iat[row, 1]):
                # TODO use regexp for 'Détail des opérations',
                # should be better .. (?)
                # Find col for credit and for debit
                is_col_credit = False
                is_col_debit = False
                for col in range(2, cols_nb):
                    if "Crédit" in td.iat[row, col]:
                        is_col_credit = True
                    if "Débit" in td.iat[row, col]:
                        is_col_debit = True
                if is_col_credit and is_col_debit:
                    table_to_analyse = True
                    break

        if not table_to_analyse:
            continue

        # for all lines
        for row in range(rows_nb):
            if td.iat[row, 0] == "Date" and \
             ("Détail des opérations" in td.iat[row, 1]):
                # TODO use regexp for 'Détail des opérations',
                #  should be better .. (?)
                # Find col for credit and for debit
                for col in range(2, cols_nb):
                    if "Crédit" in td.iat[row, col]:
                        credit_col = col
                    if "Débit" in td.iat[row, col]:
                        debit_col = col
                print_debug("Crédit at %d Débit at %d \n" % (credit_col, debit_col))
                in_table = True
            elif not in_table:
                continue
            elif td.iat[row, 0] == "" and \
              ("SOLDE PRECEDENT" in td.iat[row, 1]):
                print_debug("SOLDE PRECEDENT FOUND\n")
                in_ope = False
                if td.iat[row, credit_col] != "":
                    solde_precedent = td.iat[row, credit_col]
                else:
                    solde_precedent = td.iat[row, debit_col]
                # TODO get date

            elif td.iat[row, 0] == "" and \
             ("NOUVEAU SOLDE" in td.iat[row, 1]):
                print_debug("NOUVEAU SOLDE FOUND\n")
                in_ope = False
                if td.iat[row, credit_col] != "":
                    solde_nouveau = td.iat[row, credit_col]
                else:
                    solde_nouveau = td.iat[row, debit_col]
                # TODO get date
                # After this line, no more in Operations table
                in_table = False
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

    print_debug("---------------------------------\n\n")
    print_debug("------------nb_mvnt =%d---------------------\n\n" % (nb_mvnt))
    print_debug(mvnt_list)

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


def extract_write(inputfile, outputfile):
    # tables = camelot.read_pdf(inputfile, pages='all', flavor='stream',
    #                          table_regions=[cc_table_regions_062018],
    #                          columns=[cc_columns_sep_062018],
    #                          split_text = True)
    tables = camelot.read_pdf(inputfile, pages='all', flavor='stream',
                             table_regions=[cc_table_regions_before_062018],
                             columns=[cc_columns_sep_before_062018],
                             split_text = True)
    print_debug1(tables)
    solde, mvnt_list = treat_tables_ccFormat(tables)
    # Check that solde nouveau and solde precedent are present, if not, WARNING
    if solde['solde_precedent_montant'] == 0:
        print("WARNING : PARSING FAILED TO FIND SOLDE PRECEDENT => \
        YOU HAVE TO FIX JSON FILE !!!")
    if solde['solde_nouveau_montant'] == 0:
        print("WARNING : PARSING FAILED TO FIND SOLDE NOUVEAU => \
        YOU HAVE TO FIX JSON FILE !!!")
    write_file(solde, mvnt_list, type, outputfile)

def usage():
    print(" CLI programm to extract Credit Cooperatif Bank data from PDF.\n \
    Extraction is writen in JSON.\n \
     Usage : $ extract-cc-pdf -i  <inputfile.pdf>/ -f <files> -t <type> -o <outputfile.json>\n \
     Extract data from inputfile.pdf and write them in type (json) format \
     in outputfile.json\n \
     Files is a file containing path to several PDF file to treat in batch.\n \
     In this case output name are input file name + a json suffix.\n \
     -i/--ifile \n \
     -o/--ofile \n \
     -f/--files \n \
     -h/--help prints this message \n \
     -d/--debug add debug prints")


if __name__ == "__main__":
    inputfile = ""
    outputfile = ""
    files = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                    "dhi:o:t:f:",
                    ["debug", "help", "ifile=", "ofile=", "type=", "files="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-f", "--files"):
            files = arg
        elif opt in ("-i", "--ifile"):
            # PDF file to extract tables from
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-t", "--type"):
            type = "json"  # TODO
    if args or len(opts) > 3:
        usage()
        sys.exit()
    if files != "":
        if inputfile != "" or outputfile != "":
            usage()
            sys.exit()
    elif inputfile == "" or outputfile == "":
        usage()
        sys.exit()
    # TODO check that is a file, we can open, that is a PDF

    if files != "":
        # loop po n files path contained in Files
        with open(files, 'r') as f:
            for line in f:
                clean_line = line.strip()
                print_debug("--"+clean_line+"--")
                if clean_line != "":
                    inputfile = clean_line
                    outputfile = clean_line+".json"
                    extract_write(inputfile, outputfile)
    else:
        extract_write(inputfile, outputfile)
