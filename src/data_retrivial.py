import re, tarfile, shutil, os, urllib, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from glob import glob
import sqlalchemy as db

bases_dila = ['INCA', 'CASS', 'CAPP', 'JADE']

def data_colector(BASE:str, data_path:str):
    """
    Télécharge, décompresse et récupère les fichiers XML des décisions à partir du protocole ftp de la base.
    Parameters
    __________
    BASE: str
        Nom de base à télécharger parmi la liste suivante ['INCA', 'CASS', 'CAPP', 'JADE']
    data_path: str
        Filepath du dossier d'accueil local
    """
    assert BASE in bases_dila

    BASE_URL = "https://echanges.dila.gouv.fr/OPENDATA/" + BASE + '/'

    ### Directory creation
    base_path = os.path.join(data_path, BASE)
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    zip_path = os.path.join(base_path, 'zip')
    if not os.path.exists(zip_path):
        os.mkdir(zip_path)

    extract_path = os.path.join(base_path, 'extract')
    if not os.path.exists(extract_path):
        os.mkdir(extract_path)

    files_path = os.path.join(base_path, 'files')
    if not os.path.exists(files_path):
        os.mkdir(files_path)

    ### Request
    response = requests.get(BASE_URL)
    print(f'Reponse status code: {response.status_code}')

    source = BeautifulSoup(response.text, "html.parser")
    url = source.find_all('a', href=True)
    zip_files = [link.text for link in url if link.text.endswith('.tar.gz')]

    zip_to_download = list(set(zip_files) - set(os.listdir(zip_path)))

    if len(zip_to_download) == 0:
        print('No new files to download.')

    else:
        print(f'Zip online: {len(zip_files)}\nZip to download: {len(zip_to_download)}')

        print('\n-----Download-----')
        for file in tqdm(zip_to_download):
            data = urllib.request.urlopen(BASE_URL + file, timeout=900)
            zip_file_path = os.path.join(zip_path, file)
            with open(zip_file_path, 'wb') as f:
                f.write(data.read())

        ante_extract_files = os.listdir(extract_path)

        print('\n-----Extraction-----')
        for file in tqdm(zip_to_download):
            if not os.path.exists(os.path.join(extract_path, re.findall('[0-9]*-[0-9]*', file)[0])):
                tar = tarfile.open(os.path.join(zip_path, file))
                tar.extractall(extract_path)
                tar.close()

        new_extract_files = list(set(os.listdir(extract_path)) - set(ante_extract_files))

        print('\n-----Files Retrivial-----')
        files = 0
        for file in tqdm(new_extract_files):
            for root_, dirs_, files_ in os.walk(os.path.join(extract_path, file)):
                for f in files_:
                    if f != [] and f not in os.listdir(files_path):
                        shutil.copy2(os.path.join(root_, f), files_path)
                        files += 1
        print(f'Files: {files}')

    print('\n---Remove no xml files---')
    for file in os.listdir(files_path):
        if not file.endswith('.xml'):
            print(f'Remove: {file}')
            os.remove(os.path.join(files_path, file))

def cleaning(data):

    if not data:
        data = 'null'
    else:
        data = ['null' if x == None else x for x in data]
        data = ' '.join(data)

    return data

def data_scrapper(data_path: str, tags:list, BASE: str, sql_base: str):
    """
    Scrappe les fichiers XML des décisions de justice et les importe dans une base SQL.
    Parameters
    __________
    data_path: str
        Filepath du dossier local où se trouve les décisions
    tags: list
        Tags XML que vous souhaitez récupérer (les textes se trouve dans *CONTENU* et les labels dans *SCT*)
    BASE: str
        Nom de la base
    Sql_base: str
        Filepath de la base SQL dans laquelle vous souhaitez enregistrer le résultat du scrapping
     """
    DATABASE_URL = 'sqlite:///' + sql_base
    engine = db.create_engine(DATABASE_URL, echo = False)
    connection = engine.connect()

    filelist = glob(data_path + BASE + 'files/*.xml')

    for file in tqdm(filelist):
        tree = ET.parse(file)
        root = tree.getroot()
        row = {}
        for element in tags:
            if element == 'CONTENU':
                data = [[text for text in element.itertext() if text != None] for element in root.iter(element)]
                row[element] = cleaning(data[0])
            else:
                data = [element.text for element in root.iter(element) if element.text != None]
                row[element] = cleaning(data).strip()

        pd.DataFrame.from_dict([row]).to_sql(base_name, con = engine, if_exists = 'append', index = False, )
