# CASS_Doc2Vec
Classification des décisions de justice de la base DILA CASS

**Ce projet fournit des scripts python pour récupérer et scrapper les décisions de justice des bases DILA suivante: INCA, CASS, CAPP et JADE.**

Projet consistant à entrainer un classifieur de décision de justice entrainé sur la base de donnée CAPP fournie par la Direction de l'Information Légale et Administratives (DILA).

La base de données est disponible sur [ici](https://www.data.gouv.fr/fr/datasets/CASS/#_). Il s'agit d'un fonds documentaire de jurisprudence des grands arrêts de la jurisprudence judiciaire et les arrêts de la Cour de cassation. Après traitement des données, la base de donnée exploiter dans le cadre de ce projet est composée de 97678 arrêts.

# Scripts Python

Ces scripts ont été construits pour être exécutés de manière successive. <br>
<br>
* **data_retrivial.py**
Récupère et scrape les décisions de la base.<br>
<br>
**`data_colector(BASE:str, data_path:str)`**<br>
Télécharge, décompresse et récupère les fichiers XML des décisions à partir du [protocole ftp](ftp://echanges.dila.gouv.fr/CASS/).<br>
<br>
> **BASE** : nom de base à télécharger parmi la liste suivante ['INCA', 'CASS', 'CAPP', 'JADE']<br>
**data_path** : filepath du dossier d'accueil<br>

**`data_scrapper(data_path: str, tags:list, BASE: str, sql_base: str)`**<br>
Scrappe les fichiers XML des décisions de justice et les importe dans une base SQL.<br>
<br>
> **data_path** : filepath du dossier où se trouve les décisions<br>
**tags** : tags XML que vous souhaitez récupérer (les textes se trouve dans 'CONTENU' et les labels dans 'SCT')<br>
**BASE** : nom de la base<br>
**sql_base**: filepath de la base SQL dans laquelle vous souhaiter enregistrer le résultat du scrapping<br>

<br>
* **cleaner.py**
Supprime les décisions dont les tags SCT ou CONTENU sont nuls. Les labels sont sous la forme: "ACCIDENT DE LA CIRCULATION - Indemnisation -  Victime -  Préjudice corporel". Ce script créer une colonne 'label' avec uniquement le premier label et stocke les données sous la forme d'un DataFrame Pandas, enregistré dans un fichier pickle.<br>
<br>
**`sql_to_pickle(sql_base:str, path_out:str, BASE:str)`**<br>
<br>
> **sql_base**: filepath de la base SQL contienant les décisions scrapée<br>
**path_out** : filepath du dossier d'accueil du fichier pickle de sortie<br>
**BASE** : nom de la base<br>

<br>
### * **tokenizer**<br>
Créer une [pipeline Spacy](https://spacy.io/usage/processing-pipelines) qui procède au prépocessing du contenu des décisions de justice. Le preprocessing consiste dans les étapes suivantes:<br>
- tokenization
- supprime les stop words, la ponctuation, les caractères non alphabétiques et les tokens composés d'un seul caractère
- lemmatize
- supprime les accents
- passe en minuscule
<br>
**tokenizer(path_in:str, path_out:str, BASE:str)**<br>
<br>
> **path_in** : filepath du fichier pickle contenant les décisions nettoyées<br>
**data_out** : filepath du dossier d'accueil du fichier pickle de sortie<br>
**BASE** : nom de la base<br>

<br>
* **preprocessor.py**<br>
Normalise les textes en supprimant les 1% des textes les plus courts et les plus longs ainsi que les textes ayant les labels dont la fréquence est inférieure à 'mini_size_label'.

**`preparation(path_in:str, path_out:str, BASE:str, mini_size_label:int)`**<br>
> **path_in** : filepath du fichier pickle contenant les décisions nettoyées<br>
**data_out** : filepath du dossier d'accueil du fichier pickle de sortie<br>
**BASE** : nom de la base<br>
**mini_size_label** : fréquence minimal d'un label<br>

# Le model
Le modèle utilisé est un [Doc2Vec](https://radimrehurek.com/gensim/models/doc2vec.html). Ce modèle apprend des embeddings pour chacun des mots du corpus ainsi que pour chacun des documents. Une fois les embeddings appris (de taille 256), j'utilisé un modèle très basique, une [regression logistique](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html?highlight=logistic%20regression#sklearn.linear_model.LogisticRegression) pour classer les textes à leur label respectif.<br>
<br>
Le script du modèle et de son entrainement: [`d2v_classifier.py`](https://github.com/leoguillaume/CASS_Doc2Vec/blob/master/src/d2v_classifier.py)<br>

# Résultats
Sur le jeu d'entrainement arpès 5 épochs le modèle parvient à un F1-score (pondéré) de 0.58 et 0.37 sur le jeu de test. Ces résultats relativement faibles sont principalement dus au très grand nombre de label différents (579) et à leur distribution:
![](https://github.com/leoguillaume/CASS_Doc2Vec/blob/charts/label_distribution.png)
