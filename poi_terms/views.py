from django.shortcuts import render
import os
import re
from Code import preprocessing as pp
from Code import lda
from django.contrib.auth.decorators import login_required
from pathlib import Path

# Create your views here.
@login_required
def get_related_terms(request):
    if request.method == "POST":
        django_path = os.path.dirname(os.path.realpath(__file__))
        months_rev = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        date = str(request.POST["date_input"])
        phrase = request.POST["poi"].lower()
        # Validation
        if date == "" or phrase == "":
            return render(
                request,
                "poi_terms/poi_terms.html",
                {"error": "Missing one or more fields"},
            )

        date = date.split("-")

        month = months_rev[int(date[1])]
        day = date[2]
        day_int = int(date[2])
        date_new = month + day
        year = int(date[0])
        error = ""
        if year != 2017:
            error += "Tweets for that year are not found. "

        filepath = django_path + "/../POI_Analytics/" + phrase + ".txt"
        config = Path(filepath)
        if config.is_file():
            pass
        else:
            error += "Phrase does not exists, please try entering another phrase"

        print("POI : ", phrase, ": ", date)
        if error != "":
            return render(request, "poi_terms/poi_terms.html", {"error": error})

        print("Pre-processing")
        filepath = django_path + "/../Dataset3/" + month + day + ".txt"
        handle = open(filepath, "r")
        unprocessed_data = []
        for line in handle:
            tweet = line.split("|")[-1]
            if (
                phrase in tweet
                or phrase.capitalize() in tweet
                or phrase.upper() in tweet
            ):
                unprocessed_data.append(tweet.rstrip("\n"))
        handle.close()
        count = 1
        data = []
        for line in unprocessed_data:
            # print("Pre-processing tweet: ",count)
            preprocessedTweet = pp.processAll(line)
            data.append(preprocessedTweet)
            count += 1
        handle.close()

        print("Further preprocessing")
        data_words = list(lda.sent_to_words(data))

        # Get the stopwords
        stop_words = lda.build_stopwords()

        # Remove stopwords
        data_words = lda.remove_stopwords(data_words, stop_words)

        # Creating Bigrams
        bigram = lda.gensim.models.Phrases(data_words, min_count=5, threshold=50)
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
        mallet_path = (
            os.path.dirname(os.path.realpath(__file__)) + "/../mallet-2.0.8/bin/mallet"
        )
        if count < 500:
            tops = 10
        elif count >= 500 and count <= 1000:
            tops = 15
        elif count > 1000 and count <= 2000:
            tops = 25
        else:
            tops = 30
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

        print("LDA Model Build")

        df_topic_sents_keywords = lda.format_topics_sentences(
            ldamodel=ldamallet, corpus=corpus, texts=data
        )

        # Finding weight of each topic
        print("Finding Dominant topic for each tweet")
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
        doc_topics_frequency = sorted(
            doc_topics_frequency.items(), key=lambda kv: kv[1]
        )

        topic_words = set()
        count = 1
        for topic_id, frequency in doc_topics_frequency:
            if count > 3:
                break
            string = ""
            for word_id, prob in ldamallet.get_topic_terms(int(topic_id), topn=5):
                if id2word[word_id] != phrase:
                    topic_words.add(id2word[word_id])
            count += 1
        print(topic_words)

        # Visualize the topics
        filename = (
            os.path.dirname(os.path.realpath(__file__))
            + "/templates/poi_terms/visualization/"
            + phrase
            + "_"
            + date_new
            + ".html"
        )
        file = open(filename, "w")
        # pyldavis.enable_notebook()
        vis = lda.pyLDAvis.gensim.prepare(ldamallet, corpus, id2word)
        lda.pyLDAvis.save_html(vis, file)
        file.close()
        print("1")
        file = open(filename, "r")
        content = file.readlines()
        new_content = ""
        i = 0
        for line in content:
            if i == 2:
                new_content += """  <style type='text/css'>
										a.button {
									    -webkit-appearance: button;
									    -moz-appearance: button;
									    appearance: button;

									    text-decoration: none;
									    color: initial;
										}
									</style>
									<center><a href='http://localhost:8000/home/' class='button'>Home</a></center><br>
									<br>
									"""
            new_content += line
            i += 1
        print("2")
        file.close()
        file = open(filename, "w")
        file.write(new_content)
        file.close()

        return render(
            request,
            "poi_terms/poi_terms.html",
            {
                "phrase": phrase,
                "topic_words": topic_words,
                "date": phrase + "_" + date_new,
            },
        )

    else:
        return render(request, "poi_terms/poi_terms.html")


@login_required
def render_topics(request, date):
    print(date)
    filename = "poi_terms/visualization/" + date + ".html"
    return render(request, filename)
