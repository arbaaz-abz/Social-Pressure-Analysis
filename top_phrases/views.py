from django.shortcuts import render
import os
import re
import random
from Code import preprocessing as pp
from Code import lda
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def get_phrases(request):
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
                request, "top_phrases/top_phrases.html", {"error": "Missing field"}
            )
        date = date.split("-")
        month = months_rev[int(date[1])]
        day = int(date[2])
        date_new = str(month) + str(day)
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
                "top_phrases/top_phrases.html",
                {"error": "Tweets for that date are not found !"},
            )

        print("Pre-processing")

        unprocessed_data = []
        count = 0
        for line in handle:
            tweet = line.split("|")[-1]
            unprocessed_data.append(tweet.rstrip("\n"))
            count += 1

        data = []
        i = 0
        for line in unprocessed_data:
            # print("Pre-processing tweet: ",i)
            preprocessedTweet = pp.processAll(line) + "\n"
            data.append(preprocessedTweet)
            i += 1

        handle.close()
        # print("Further preprocessing")
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

        # print("Creating dictionary and corpus")

        # Create Dictionary for lda
        id2word = lda.corpora.Dictionary(data_lemmatized)

        # Create Corpus for lda
        texts = data_lemmatized

        baseline_words = []
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
        try:
            os.mkdir(root_dir)
        except:
            pass
        user_month = month
        user_date = day
        for filename in os.listdir(root_dir):
            month_f = filename[:3]
            if months[month_f] > months[user_month]:
                continue
            date_f = int(re.findall(r"\d+", filename)[0])
            if (date_f < user_date and months[month_f] == months[user_month]) or (
                months[month_f] < months[user_month]
            ):
                print(filename)
                poi_file = open(root_dir + filename)
                for phrase in poi_file:
                    baseline_words.append(phrase.rstrip("\n"))
                poi_file.close()
        # print("BASELINE WORDS: ",baseline_words)

        print("Finding Phrases of interest ...")
        # Phrase of Interest Detection , Picking only the top 20 POIs
        dict_len = len(id2word)
        phrases_scores = {}
        imp_phrases = []
        # print(texts[0])
        for i in range(dict_len):
            if id2word[i] in stop_words or id2word[i] in baseline_words:
                continue
            count = 0
            print("Processing word : ", i + 1)
            for doc in texts:
                for word in doc:
                    if id2word[i] == word:
                        count += 1
            phrases_scores[id2word[i]] = count / dict_len

        no_pois = 5
        phrases_scores_counter = lda.collections.Counter(phrases_scores)
        phrases_scores_counter = sorted(
            phrases_scores_counter.items(), key=lambda kv: kv[1]
        )
        no_of_phrases = no_pois + 1
        top_phrases = phrases_scores_counter[-1:-no_of_phrases:-1]
        for i, j in top_phrases:
            imp_phrases.append(i)
        print(imp_phrases)
        filename = (
            os.path.dirname(os.path.realpath(__file__))
            + "/../POIs/"
            + date_new
            + ".txt"
        )
        file = open(filename, "w")
        for phrase in imp_phrases:
            file.write(phrase + "\n")
        file.close()
        return render(
            request,
            "top_phrases/top_phrases.html",
            {"pois": imp_phrases, "date": month + " " + date[2]},
        )
    else:
        return render(request, "top_phrases/top_phrases.html")
