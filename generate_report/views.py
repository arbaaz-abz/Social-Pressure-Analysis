from django.shortcuts import render
import os, re, operator
from Code import preprocessing as pp
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.contrib.auth.decorators import login_required
from pathlib import Path
from django.http import HttpResponse

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from matplotlib import pyplot as plt
import matplotlib.style as style

style.use("fivethirtyeight")

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import portrait
from reportlab.platypus import Image


@login_required
def report_view(request):
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
                "generate_report/report.html",
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
            error += "Incorrect Date, Please enter a valid range."
        elif int(date_start[1]) == int(date_end[1]) and date_start_day > date_end_day:
            error += "Incorrect Date, Please enter a valid range."
        if date_start_year != 2017:
            error += "Tweets for the start year do not exist. "
        if date_end_year != 2017:
            error += "Tweets for the end year do not exist. "

        # Check if POI Exists
        phrase = request.POST["poi"].lower()
        filepath = django_path + "/../POI_Analytics/" + phrase + ".txt"
        print(filepath)
        config = Path(filepath)
        if config.is_file():
            file = open(filepath)
        else:
            error += "Phrase does not exists, please try entering another phrase"

        print(error)

        if error != "":
            return render(request, "generate_report/report.html", {"error": error})

        file_dates = open(django_path + "/" + "year_dates.txt")
        year_dates = {}
        i = 1
        for row in file_dates:
            year_dates[row.rstrip()] = i
            i += 1
        file_dates.close()

        # Analytics
        to_plot = []
        for row in file:
            date = row.split("|")[0]
            month = date[:3]
            day = int(re.findall(r"\d+", date)[0])
            date = month + str(day)
            if (
                year_dates[date] >= year_dates[date_start_month + str(date_start_day)]
                and year_dates[date] <= year_dates[date_end_month + str(date_end_day)]
            ):
                to_plot.append(row)

        # Packaging Data
        dates_x_axis = []
        weights_y_axis = []
        frequency_y_axis = []
        for row in to_plot:
            row = row.split("|")
            dates_x_axis.append(row[0])
            weights_y_axis.append(float(row[2]))
            frequency_y_axis.append(int(row[1]))
        print(dates_x_axis)
        print(weights_y_axis)
        print(frequency_y_axis)

        # Twittersphere importance and frequency of usage graph
        df = DataFrame(
            data={
                "dates": dates_x_axis,
                "twitter_importance": weights_y_axis,
                "frequency": frequency_y_axis,
            }
        )
        plt.figure(figsize=(30, 8))
        ax = sns_plot = sns.lineplot(x="dates", y="twitter_importance", data=df)
        # ax.set(ylim=(0.00,0.10))
        plt.savefig(django_path + "/templates/reports/weights.jpeg")

        plt.figure(figsize=(30, 8))
        sns_plot = sns.lineplot(x="dates", y="frequency", data=df)
        plt.savefig(django_path + "/templates/reports/frequency.jpeg")

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

        df = DataFrame(data={"sentiment": y_axis, "dates": x_axis})
        plt.figure(figsize=(30, 8))
        ax = sns_plot = sns.lineplot(x="dates", y="sentiment", data=df)
        ax.set(ylim=(-1.0, 1.0))
        plt.savefig(django_path + "/templates/reports/sentiments.jpeg")

        labels = "Postive", "Neutral", "Negative"
        sizes = [pos_count, neu_count, neg_count]
        explode = (0, 0, 0.1)
        plt.figure(figsize=(10, 6))
        fig1, ax1 = plt.subplots()
        ax1.pie(
            sizes,
            explode=explode,
            labels=labels,
            autopct="%1.1f%%",
            shadow=True,
            startangle=90,
        )
        ax1.axis("equal")
        plt.savefig(django_path + "/templates/reports/pie.jpeg")

        pdfname = django_path + "/templates/reports/" + phrase + ".pdf"

        c = canvas.Canvas(pdfname, pagesize=portrait(letter))

        # Header
        c.setFont("Helvetica", 30, leading=None)
        c.drawString(180, 740, "Phrase: " + phrase)

        # Terms
        c.setFont("Helvetica", 24, leading=None)
        date_string = (
            date_start_month
            + " "
            + str(date_start_day)
            + "  To  "
            + date_end_month
            + " "
            + str(date_end_day)
        )
        c.drawCentredString(300, 690, "Date Range: " + date_string)

        # TWITTER SPHERE IMPORTANCE
        image = django_path + "/templates/reports/weights.jpeg"
        c.setFont("Helvetica", 18, leading=None)
        c.drawCentredString(300, 630, "Twittersphere Importance over time")
        c.drawImage(image, 80, 370, width=450, height=250)

        # FREQUENCY OF usage
        image = django_path + "/templates/reports/frequency.jpeg"
        c.setFont("Helvetica", 18, leading=None)
        c.drawCentredString(300, 300, "frequency of usage")
        c.drawImage(image, 80, 40, width=450, height=250)

        c.showPage()

        # SENTIMENTS
        image = django_path + "/templates/reports/sentiments.jpeg"
        c.setFont("Helvetica", 18, leading=None)
        c.drawCentredString(300, 740, "Sentiments of the Twitter Audience")
        c.drawImage(image, 80, 480, width=450, height=250)

        # PIE CHART
        c.setFont("Helvetica", 18, leading=None)
        c.drawCentredString(
            300, 410, "General Sentiments of the Public over the entire period"
        )
        pie = django_path + "/templates/reports/pie.jpeg"
        c.drawImage(pie, 150, 130, width=300, height=270)
        c.showPage()

        height = 740
        for date, dictionary in date_usr_loca.items():
            c.setFont("Helvetica", 19, leading=None)
            c.drawCentredString(300, height, "Most negative user's on " + date)
            c.setFont("Helvetica", 12, leading=None)
            height = height - 30
            for index, user_loca in dictionary.items():
                c.drawCentredString(300, height, str(index) + ". " + str(user_loca))
                height = height - 20
            height = height - 40
            if height < 300:
                c.showPage()
                height = 740

        c.save()
        print(date_usr_loca)
        return render(request, "generate_report/display_report.html", {"link": phrase})

    else:
        return render(request, "generate_report/report.html")


@login_required
def display_report(request):
    if request.method == "POST":
        django_path = os.path.dirname(os.path.realpath(__file__))
        filename = (
            django_path + "/templates/reports/" + request.POST["pdfname"] + ".pdf"
        )
        file = open(filename, "rb")
        response = HttpResponse(file, content_type="application/pdf")
        response["Content-Distribution"] = "attachment; filename={}".format(filename)
        return response
    else:
        return render(
            request,
            "generate_report/report.html",
            {"error": "Please generate the report first"},
        )
