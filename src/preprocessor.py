
import random
import pandas as pd

def preparation(path_in:str, path_out:str, BASE:str, mini_size_label:int):

    print('\n-----Importing Data------')
    df = pd.read_pickle(path_in)

    print('\n-----Data preparation-----')
    lenghts = [len(text) for text in df.token]
    df = df[(df.token.map(len) > pd.Series(lenghts).quantile(0.01)) & (df.token.map(len) < pd.Series(lenghts).quantile(0.99))]

    M = df.label.value_counts()[df.label.value_counts() <= mini_size_label].index.tolist()
    df = df[~ df.label.isin(M)]

    label_95 = df.label.value_counts()[df.label.value_counts() > df.label.value_counts().quantile(0.95)].index.tolist()
    L = int(df.label.value_counts().quantile(0.95))
    D = list()
    for label in label_95:
        D += random.sample(df[df.label == label].ID.values.tolist(), len(df[df.label == label]) - L)

    df = df[~ df.ID.isin(D)]

    print('\n--------Saving Data-------')
    df.to_pickle(path_out + BASE + '_prepared.pkl')
