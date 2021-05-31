import pandas as pd
import collections
import os

# from pprint import pprint

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.models.ldamodel import LdaModel

# spacy for lemmatization
import spacy

# Plottting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this

#%matplotlib inline

# Enable logging for gensim - optional
import logging

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.ERROR
)

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from nltk.corpus import stopwords

nlp = spacy.load("en", disable=["parser", "ner"])


def sent_to_words(sentences):
    for sentence in sentences:
        yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))


def remove_stopwords(texts, stop_words):
    return [
        [word for word in simple_preprocess(str(doc)) if word.lower() not in stop_words]
        for doc in texts
    ]


def make_bigrams(texts, bigram):
    return [bigram[doc] for doc in texts]


def lemmatization(texts, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append(
            [token.lemma_ for token in doc if token.pos_ in allowed_postags]
        )
    return texts_out


def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(
                    pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]),
                    ignore_index=True,
                )
            else:
                break
    sent_topics_df.columns = ["Dominant_Topic", "Perc_Contribution", "Topic_Keywords"]

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return sent_topics_df


def convertldaGenToldaMallet(mallet_model):
    model_gensim = LdaModel(
        id2word=mallet_model.id2word,
        num_topics=mallet_model.num_topics,
        alpha=mallet_model.alpha,
        eta=0,
    )
    model_gensim.state.sstats[...] = mallet_model.wordtopics
    model_gensim.sync_state()
    return model_gensim


def build_stopwords():
    handle = open(os.path.dirname(os.path.realpath(__file__)) + "/stopwords.txt", "r")
    stopword_list = list(stopwords.words("english"))
    for word in handle:
        word = word.strip()
        # word = word.split()[0]
        if word not in stopword_list:
            stopword_list.append(word)
    stopword_list.extend(
        [
            "RT",
            "lose",
            "https",
            "htt",
            "http",
            "https",
            "ps",
            "able",
            "come",
            "happen",
            "reach",
            "anyway",
            "tell",
            "ahead",
            "hold",
            "try",
        ]
    )
    return stopword_list
