print("Importing")
import preprocessing as pp
import lda

print("Pre-processing")
filename = "../Dataset/Aug10_tweets.txt"
handle = open(filename, "r")
unprocessed_data = []
i = 1
for line in handle:
    tweet = line.split(",", 4)[-1]
    unprocessed_data.append(tweet.rstrip())

count = 1
data = []
for line in unprocessed_data:
    print("Pre-processing tweet: ", count)
    print(line)
    preprocessedTweet = pp.processAll(line) + "\n"
    data.append(preprocessedTweet)
    count += 1
handle.close()

data_words = list(lda.sent_to_words(data))

# Get the stopwords
stop_words = lda.build_stopwords()

# Remove stopwords
data_words = lda.remove_stopwords(data_words, stop_words)

# Creating Bigrams
bigram = lda.gensim.models.Phrases(data_words, min_count=5, threshold=100)
data_words_bigrams = lda.make_bigrams(data_words, bigram)

# Lemmatization
data_lemmatized = lda.lemmatization(
    data_words_bigrams, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]
)

print("Creating dictionary and corpus")

# Create Dictionary for lda
id2word = lda.corpora.Dictionary(data_lemmatized)

# Create Corpus for lda
texts = data_lemmatized

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# lda MALLET
mallet_path = "../mallet-2.0.8/bin/mallet"
tops = 15
print("Buildaing lda Model..")
ldamallet = lda.gensim.models.wrappers.LdaMallet(
    mallet_path, corpus=corpus, num_topics=tops, id2word=id2word
)

# Compute Coherence Score
coherence_model_ldamallet = lda.CoherenceModel(
    model=ldamallet, texts=data_lemmatized, dictionary=id2word, coherence="c_v"
)
coherence_ldamallet = coherence_model_ldamallet.get_coherence()
print("\nCoherence Score: ", coherence_ldamallet)
ldamallet = lda.convertldaGenToldaMallet(ldamallet)

print("Finding Dominant Topics")
df_topic_sents_keywords = lda.format_topics_sentences(
    ldamodel=ldamallet, corpus=corpus, texts=data
)

# Format
df_dominant_topic = df_topic_sents_keywords.reset_index()
df_dominant_topic.columns = [
    "Document_No",
    "Dominant_Topic",
    "Topic_Perc_Contrib",
    "Keywords",
    "Text",
]

doc_topics = list(df_dominant_topic["Dominant_Topic"])
doc_topics_frequency = lda.collections.Counter(doc_topics)
doc_topics_frequency = sorted(doc_topics_frequency.items(), key=lambda kv: kv[1])
# Top Topics = 55
doc_topics_frequency = doc_topics_frequency[-1:-4:-1]
top_topics = []
for i in range(len(doc_topics_frequency)):
    top_topics.append(int(doc_topics_frequency[i][0]))


print("TOP 3 TOPICS : ")
for i in top_topics:
    print("TOPIC ", i + 1, end=" : ")
    relavent_words = ldamallet.get_topic_terms(int(i), topn=10)
    for word_id, prob in relavent_words:
        print(id2word[word_id], end="|")
    print("\n-------------------------------------")

# Visualize the topics
filename = "visualization" + "_Aug10" + ".html"
file = open(filename, "w")
# pyldavis.enable_notebook()
vis = lda.pyLDAvis.gensim.prepare(ldamallet, corpus, id2word)
lda.pyLDAvis.save_html(vis, file)
