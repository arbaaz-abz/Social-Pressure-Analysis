from django.shortcuts import render
import os
import re
from Code import preprocessing as pp
from Code import lda
from django.contrib.auth.decorators import login_required
from pathlib import Path

# Create your views here.
@login_required
def macro_model(request):
    if request.method == "POST":
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
        date = str(request.POST["date"])
        if date == "":
            return render(
                request, "trending_topics/macro_lda.html", {"error": "Missing field"}
            )
        date = date.split("-")
        month = months_rev[int(date[1])]
        day = int(date[2])
        date_new = str(month) + str(date[2])
        year = int(date[0])

        if year != 2017:
            return render(
                request,
                "top_phrases/top_phrases.html",
                {"error": "Tweets for that year are not found !"},
            )

        filename = (
            os.path.dirname(os.path.realpath(__file__))
            + "/../Dataset3/"
            + month
            + date[2]
            + ".txt"
        )
        try:
            handle = open(filename, "r")
        except IOError:
            print("Could not read file !")
            return render(
                request,
                "trending_topics/macro_lda.html",
                {"error": "Tweets for that date are not found !"},
            )
        unprocessed_data = []
        i = 1
        for line in handle:
            tweet = line.split("|")[-1]
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
        bigram = lda.gensim.models.Phrases(data_words, min_count=5, threshold=75)
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
            tops = 8
        elif count >= 500 and count <= 1000:
            tops = 20
        elif count > 1000 and count <= 2000:
            tops = 30
        elif count > 2000 and count <= 5000:
            tops = 35
        else:
            tops = 40
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

        pois = {}
        months = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }
        root_dir = os.path.dirname(os.path.realpath(__file__)) + "/../POIs/"
        user_month = month
        user_date = day
        for filename in os.listdir(root_dir):
            month_f = filename[:3]
            if months[month_f] > months[user_month]:
                continue
            date_f = int(re.findall(r"\d+", filename)[0])
            if (date_f <= user_date and months[month_f] == months[user_month]) or (
                months[month_f] < months[user_month]
            ):
                print(filename)
                poi_file = open(root_dir + filename)
                for phrase in poi_file:
                    pois[phrase.rstrip("\n")] = month_f + " " + str(date_f)
                poi_file.close()

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
        total = len(doc_topics)
        topic_weights = {}
        for topic_id, frequency in doc_topics_frequency:
            topic_weights[topic_id] = frequency / total

        def get_doc_topics(lda_model, bow):
            gamma, _ = lda_model.inference([bow])
            topic_dist = gamma[0] / sum(gamma[0])
            return [
                (topic_id, topic_value)
                for topic_id, topic_value in enumerate(topic_dist)
            ]

        print("Obtaining Analytics for each POI on : ", date_new)
        for poi in pois:

            # Frequency of usage on this day
            poi_frequency = 0
            filename = "/../Dataset3/" + month + date[2] + ".txt"
            handle = open(os.path.dirname(os.path.realpath(__file__)) + filename, "r")
            for tweet in handle:
                if poi in tweet or poi.capitalize() in tweet or poi.upper() in tweet:
                    poi_frequency += 1
            handle.close()

            # Skip the POI if it was never user during a particular day
            if poi_frequency != 0:

                # Finding which topic a word belongs to most probably
                bow = id2word.doc2bow([poi])
                doc_lda = get_doc_topics(ldamallet, bow)
                dense_vec = lda.gensim.matutils.sparse2full(
                    doc_lda, ldamallet.num_topics
                )
                highest = 0
                total = 0

                for index in range(len(dense_vec)):
                    total += dense_vec[index]
                    if dense_vec[index] > highest:
                        highest = dense_vec[index]
                        topic_id = index
                # print("POI : ",poi,", Topic : ",topic_id+1,", Prob : ",highest)

                # Find the topic weight
                poi_topic_weight = topic_weights[topic_id]

                # Related Terms
                relavent_words = ldamallet.get_topic_terms(topic_id, topn=6)
                top_words = ""
                for word_id, prob in relavent_words:
                    if id2word[word_id] != poi:
                        top_words += id2word[word_id] + ","
                top_words = top_words[:-1]

                to_write = (
                    month
                    + date[2]
                    + "|"
                    + str(poi_frequency)
                    + "|"
                    + str(poi_topic_weight)
                    + "|"
                    + top_words
                    + "\n"
                )
                print("PHRASE ", poi, " : ", to_write)

            else:
                to_write = (
                    month + date[2] + "|" + str(0) + "|" + str(0) + "|" + "Nil" + "\n"
                )
                # print("PHRASE ",poi," : ",to_write)

            # Write to a file
            try:
                os.mkdir(
                    os.path.dirname(os.path.realpath(__file__)) + "/../POI_Analytics/"
                )
            except:
                pass
            filepath = (
                os.path.dirname(os.path.realpath(__file__))
                + "/../POI_Analytics/"
                + poi
                + ".txt"
            )
            config = Path(filepath)
            if config.is_file():
                print("File Exists")
                file = open(filepath)
                file_contents = []
                for row in file:
                    file_contents.append(row.rstrip("\n"))
                file.close()
                file = open(filepath, "w")
                print("PREVIOUS CONTENTS : ", file_contents)
                flag = 0
                for row in file_contents:
                    if row.split("|")[0] == date_new:
                        print("WROTE : ", to_write)
                        file.write(to_write)
                        flag = 1
                    else:
                        print("WROTE : ", row)
                        file.write(row + "\n")
                if flag == 0:
                    file.write(to_write)
                    print("WROTE : ", to_write)
                file.close()
            else:
                print("File Does not Exists")
                file = open(filepath, "w")
                file.write(to_write)
                file.close()
            print("*" * 20)

        # Visualize the topics
        filename = (
            os.path.dirname(os.path.realpath(__file__))
            + "/templates/trending_topics/visualization/"
            + date_new
            + ".html"
        )
        file = open(filename, "w")
        # pyldavis.enable_notebook()
        vis = lda.pyLDAvis.gensim.prepare(ldamallet, corpus, id2word)
        lda.pyLDAvis.save_html(vis, file)
        file.close()

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
									<center><a href='~' class='button'>Home</a></center><br>
									<br>
									"""
            new_content += line
            i += 1
        file.close()
        file = open(filename, "w")
        file.write(new_content)
        file.close()

        filename = "trending_topics/visualization/" + date_new + ".html"

        return render(
            request,
            "trending_topics/macro_lda.html",
            {"topic_weights": topic_weights, "filename": filename, "date": date_new},
        )
    else:
        return render(request, "trending_topics/macro_lda.html")


@login_required
def render_topics(request, date):
    print(date)
    filename = "trending_topics/visualization/" + str(date) + ".html"
    return render(request, filename)
