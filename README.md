# Introduction

Le but des programmes python de ce dépôt est de pouvoir extraire les informations
de mouvements bancaire issues du Relevé PDF fourni par le Crédit Coopératif.

Malheureusement le Crédit Coopératif ne fourni pas d'extrait des opérations bancaires
autrement que sous le format PDF, très dommage pour une banque qui est quasi
une banque en ligne.

Il est donc impossible d'intégrer ces données dans un logiciel de comptabilité
ou de les traiter de façon informatique.

Le programme **extract-cc-pdf.py** permet d'extraire les données (au format JSON
pour le moment).

Ce programme utilise la librairie **camelot** pour extraire les informations sous
forme de tableaux.

Le programme **plot_cc_operations.py** utilise matplotlib et le fichier issu de
**extract-cc-pdf.py** pour tracer une courbe des opérations bancaires.

Il est possible de fournir une liste de fichiers PDF à **extract-cc-pdf.py**
qui créera des fichiers JSON correspondant puis de donner à **plot_cc_operations.py**
un fichier contenant la liste des fichiers JSON. Ainsi on peut avoir la courbe
d'évolution du compte bancaire sur plusieurs mois.

Les relevés du Crédit Coopératif semblent suivre 2 formats différents, le changement
a eu lieu au mois de Juin 2018.
Les données ne sont pas présentées de la même façon dans les 2 formats.


# Installation

Packages requis :
- camelot-py
- matplotlib
- pandas


# Usage

```
$ extract-cc-pdf -i  <inputfile.pdf>/ -f <files> -t <type> -o <outputfile.json>
Extract data from inputfile.pdf and write them in type (json) format
in outputfile.json

Files is a file containing path to several PDF file to treat in batch.
In this case output name are input file name + a json suffix.
-i/--ifile
-o/--ofile
-f/--files
-h/--help prints this message
-d/--debug add debug prints"

```

```
$ plot-cc-operations -i <inputfile>
     where inputfile is a JSON file or
$ plot-cc-operations -f <files>
     where files contains paths of input files in JSON
     -d/--debug : print debug info
     -h/--help : print this message
```

Exemples :
```
./extract-cc-pdf.py -i data/RELEVES_20191001.pdf -o data/RELEVES_20191001.json
```
suivi de :
```
./plot_cc_operations.py -i data/RELEVES_20191001.json
```

ou alors

```
cat filesPDF
data/RELEVES_20191001.pdf
data/RELEVES_20191101.pdf
data/RELEVES_20191202.pdf
data/RELEVES_20200102.pdf
data/RELEVES_20200201.pdf
```
```
./extract-cc-pdf.py -f filesPDF
```

```
cat filesPDF_extractJSON
data/RELEVES_0902258281_20191001.pdf.json
data/RELEVES_0902258281_20191101.pdf.json
data/RELEVES_0902258281_20191202.pdf.json
data/RELEVES_0902258281_20200102.pdf.json
data/RELEVES_0902258281_20200201.pdf.json
```
suivi de
```
./plot_cc_operations.py -f filesPDF_extractJSON
```
cette dernière opération tracera l'évolution du compte pour les mois de Octobre
2019 à Février 2020.



# Architecture

Le programme d'extraction utilise camelot-py pour trouver les tables dans le PDF.

Pour avoir un meilleur résultat il a fallu paramétrer l'appel à camelot pour
lui donner une région où chercher les tables (éviter des Header de page) et
lui donner les coordonnées des séparateurs de colonnes.

Les coordonnées passées pour les *table_regions* et les *columns* sont exprimés
en coordonnées PDF, relevées en utilisant l'outils GhostView (gv).

Camelot-py renvoie des tables que l'on traitent ensuite grâce à la connaissance
du format.
Si la table est une table contenant des données sur les opérations bancaires on
les extrait.
On extrait également le solde au début de relevé et le solde en fin de relevé.


# TODO

- Faire l'extraction vers du CSV
- Faire l'extraction pour le format PDF d'avant Juin 2018
