from django.shortcuts import render
import os
import re
import operator
from django.contrib.auth.decorators import login_required
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Code import preprocessing as pp
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from matplotlib import pyplot as plt
import matplotlib.style as style

style.use("fivethirtyeight")

# Create your views here.
@login_required
def get_sentiment(request):
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
        date_start = str(request.POST["date1"])
        date_end = str(request.POST["date2"])
        phrase = request.POST["poi"].lower()

        # Validation
        if date_start == "" or phrase == "" or date_end == "":
            return render(
                request,
                "sentiment_phrase/sentiment_phrase.html",
                {"error": "Missing one or more fields"},
            )
        date_start = date_start.split("-")
        date_end = date_end.split("-")

        date_start_month = months_rev[int(date_start[1])]
        date_start_day = int(date_start[2])
        date_start_year = int(date_start[0])

        date_end_month = months_rev[int(date_end[1])]
        date_end_day = int(date_end[2])
        date_end_year = int(date_start[0])

        error = ""
        if int(date_start[1]) > int(date_end[1]):
            error += "Incorrect Date, Please enter a valid range. "
        elif int(date_start[1]) == int(date_end[1]) and date_start_day > date_end_day:
            error += "Incorrect Date, Please enter a valid range. "
        if date_start_year != 2017:
            error += "Tweets for the start year do not exist. "
        if date_end_year != 2017:
            error += "Tweets for the end year do not exist. "

        phrase = request.POST["poi"].lower()
        filepath = django_path + "/../POI_Analytics/" + phrase + ".txt"
        print(filepath)
        config = Path(filepath)
        if config.is_file():
            pass
        else:
            error += "Phrase does not exists"

        if error != "":
            return render(
                request, "sentiment_phrase/sentiment_phrase.html", {"error": error}
            )

        print("POI : ", phrase, " from ", date_start, " to ", date_end)
        file_dates = open(django_path + "/" + "year_dates.txt")
        year_dates = {}
        i = 1
        for row in file_dates:
            year_dates[row.rstrip()] = i
            i += 1
        file_dates.close()

        analyzer = SentimentIntensityAnalyzer()
        points = {}

        date_usr_loca = {}

        def format_data(data):
            usr_loca_dict = dict(sorted(data.items(), key=operator.itemgetter(1)))
            return usr_loca_dict

        dataset_path = django_path + "/../Dataset3/"
        index_file = open(django_path + "/../" + "index.txt")
        pos_count = 0
        neg_count = 0
        neu_count = 0
        for filename in index_file:
            filename = filename.rstrip("\n")
            month = filename[:3]
            day = int(re.findall(r"\d+", filename)[0])
            date = month + str(day)
            if (
                year_dates[date] >= year_dates[date_start_month + str(date_start_day)]
                and year_dates[date] <= year_dates[date_end_month + str(date_end_day)]
            ):
                print(filename)
                data = {}
                handle = open(dataset_path + filename + ".txt")
                total = 0
                count = 0
                for sentence in handle:
                    sentence_split = sentence.split("|")
                    tweet = sentence_split[-1]
                    process_tweet = pp.processAll(tweet)
                    if (
                        phrase in process_tweet
                        or phrase.capitalize() in process_tweet
                        or phrase.upper() in process_tweet
                    ):
                        vs = analyzer.polarity_scores(process_tweet)
                        # print(vs['compound'])
                        total = total + vs["compound"]
                        count = count + 1
                        if vs["compound"] < -0.2:
                            neg_count += 1
                        elif vs["compound"] >= -0.2 and vs["compound"] <= 0.2:
                            neu_count += 1
                        else:
                            pos_count += 1

                        if (
                            vs["compound"] < -0.5
                            and sentence_split[2] != ""
                            and sentence_split[1] != ""
                        ):
                            usr = re.sub(r"\n", "", sentence_split[2])
                            loca = re.sub(r"\n", "", sentence_split[1])
                            if (usr, loca) in data.keys():
                                data[(usr, loca)] = (
                                    data[(usr, loca)] + vs["compound"]
                                ) / 2
                            else:
                                data[(usr, loca)] = vs["compound"]
                handle.close()
                data = format_data(data)
                # print(data)
                if count == 0:
                    print("Phrase not found")
                    points[day] = 0
                    continue
                to_append = {}
                if len(data) != 0:
                    counter = 1
                    for usr_loca, score in data.items():
                        if counter > 5:
                            break
                        to_append[counter] = usr_loca
                        counter += 1
                    date_usr_loca[date] = to_append
                res = total / count
                print(res)
                points[date] = res
        # print(points)
        # print(date_usr_loca)
        x_axis = list(points.keys())
        y_axis = list(points.values())
        return render(
            request,
            "sentiment_phrase/sentiment_phrase.html",
            {
                "phrase": phrase,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "start_date": date_start,
                "end_date": date_end,
                "date_usr_loca": date_usr_loca,
                "pie_data": [pos_count, neu_count, neg_count],
            },
        )
    else:
        return render(request, "sentiment_phrase/sentiment_phrase.html")
