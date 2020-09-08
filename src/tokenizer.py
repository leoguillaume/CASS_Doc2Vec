import pandas as pd
from unidecode import unidecode
from tqdm import tqdm
import spacy

def preprocessing(doc):
    doc = [unidecode(token.lemma_).lower() for token in doc \
           if not token.is_stop \
           and not token.is_punct \
           and token.is_alpha \
           and len(token) > 1]
    return doc

nlp = spacy.load("fr_core_news_md")
nlp.add_pipe(preprocessing, after = 'parser')

def tokenizer(path_in:str, path_out:str, BASE:str):
    df = pd.read_pickle(path_in)
    docs = nlp.pipe(df.CONTENU, disable = 'ner', batch_size = 20)
    tokens = list()

    print('\n---Preprocessing Texts---')
    for doc in tqdm(docs):
        tokens.append(doc)
    df['token'] = tokens

    print('\n-------Save tokens------')
    df.to_pickle(path_out + BASE + '_tokenized.pkl' )
