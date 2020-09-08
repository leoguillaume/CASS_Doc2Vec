import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from gensim.models.doc2vec import TaggedDocument
from sklearn.metrics import f1_score
from gensim.test.utils import get_tmpfile
from gensim.models import Doc2Vec

class CustomDoc2Vec():
    def __init__(self, docs, **kwargs):
        self.docs = docs
        self.tags = [doc.tags for doc in self.docs]
        self.model = Doc2Vec(**kwargs)
        self.vectors = [self._get_vector(tag[0]) for tag in self.tags]
        self.epochs = 5

    def _get_vector(self, tag):
        return self.model.docvecs[tag]

    def fit(self, epochs = 1):
        self.epochs += epochs
        self.model.train(self.docs, total_examples = self.model.corpus_count, epochs = epochs)
        self.vectors = [self._get_vector(tag[0]) for tag in self.tags]

    def predict(self, X=None):
        return [self.model.infer_vector(doc) for doc in X.token]

# First train of Doc2vec and predictions with a LogisticRegression classifier

d2v = CustomDoc2Vec(docs = tagged_docs, **params)
epochs = list()
score_train = list()
score_test = list()

vec_train = d2v.vectors
vec_test = d2v.predict(X_test)

lr = LogisticRegression(multi_class = 'multinomial', random_state = seed, max_iter = 200)
lr.fit(d2v.vectors, y_train)
y_train_pred = lr.predict(vec_train)
y_test_pred = lr.predict(vec_test)

score_train.append(f1_score(y_train, y_train_pred, average = 'weighted'))
score_test.append(f1_score(y_test, y_test_pred, average = 'weighted'))
epochs.append(d2v.epochs)

df = pd.read_pickle('CASS_prepared.pkl')
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1, random_state = seed)
X = df[['ID', 'token']]
y = df.label

seed = 42

tagged_docs = [TaggedDocument(row.token, [row.ID]) for index, row in X_train.iterrows()]

params = {'documents': tagged_docs,
          'vector_size': 256,
          'seed': seed,
          'dbow_words': 1,
          'min_count': 3}
          
## Retrain Doc2Vec

for epoch in range(7):
    d2v.fit()
    vec_train = d2v.vectors
    vec_test = d2v.predict(X_test)

    lr = LogisticRegression(multi_class = 'multinomial', random_state = seed, max_iter = 200)
    lr.fit(d2v.vectors, y_train)
    y_train_pred = lr.predict(vec_train)
    y_test_pred = lr.predict(vec_test)

    score_train.append(f1_score(y_train, y_train_pred, average = 'weighted'))
    score_test.append(f1_score(y_test, y_test_pred, average = 'weighted'))
    epochs.append(d2v.epochs)
    print(f'Epoch {d2v.epochs} done at {current_time}.')
