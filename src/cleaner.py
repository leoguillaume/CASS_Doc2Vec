import pandas as pd
import numpy as np
import re, unidecode
import sqlalchemy as db

def label(text):
    text = text.split(' - ')[0]
    text = re.sub('\((.*)\)', '', text)
    text = re.sub('[^A-Z\s-]', '', text).strip()
    text = re.sub('\s{2,}', ' ', text)
    return text

def sql_to_pickle(sql_base:str, path_out:str, BASE:str):

    DATABASE_URL = 'sqlite:///' + sql_base
    engine = db.create_engine(DATABASE_URL, echo = False)
    connection = engine.connect()

    df = pd.read_sql(BASE, con = engine)
    df = df.replace('null', np.NaN)
    df.drop_duplicates(subset = 'CONTENU', inplace = True)
    df.dropna(subset = ['SCT'], inplace = True)
    df.dropna(subset = ['CONTENU'], inplace = True)
    df['label'] = df.SCT.apply(label)
    df.dropna(subset = ['label'] inplace = True)

    print('\n--------Saving Data-------')
    df.to_pickle(path_out + BASE + '.pkl')
