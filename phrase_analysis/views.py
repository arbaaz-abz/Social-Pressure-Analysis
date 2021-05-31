from django.shortcuts import render
import os
import re
from Code import preprocessing as pp
from Code import lda
from django.contrib.auth.decorators import login_required
from pathlib import Path


@login_required
def phrase_analysis_view(request):
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
                "phrase_analysis/phrase_analysis.html",
                {"error": "Missing one or more fields"},
            )

        date_start = date_start.split("-")
        date_end = date_end.split("-")

        date_start_month = months_rev[int(date_start[1])]
        date_start_day = int(date_start[2])
        date_start_year = int(date_start[0])

        date_end_month = months_rev[int(date_end[1])]
        date_end_day = int(date_end[2])
        date_end_year = int(date_end[0])

        error = ""
        if int(date_start[1]) > int(date_end[1]):
            error += "Incorrect Date, Please enter a valid range. "
        elif int(date_start[1]) == int(date_end[1]) and date_start_day > date_end_day:
            error += "Incorrect Date, Please enter a valid range. "
        if date_start_year != 2017:
            error += "Tweets for the start year do not exist. "
        if date_end_year != 2017:
            error += "Tweets for the end year do not exist. "

        # Check if POI Exists
        poi = request.POST["poi"].lower()
        filepath = django_path + "/../POI_Analytics/" + poi + ".txt"
        print(filepath)
        config = Path(filepath)
        if config.is_file():
            file = open(filepath)
        else:
            error += "Phrase does not exists."

        print(error)

        if error != "":
            return render(
                request, "phrase_analysis/phrase_analysis.html", {"error": error}
            )

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

        return render(
            request,
            "phrase_analysis/phrase_analysis.html",
            {
                "dates_x_axis": dates_x_axis,
                "weights_y_axis": weights_y_axis,
                "frequency_y_axis": frequency_y_axis,
                "poi": poi,
                "start_date": date_start,
                "end_date": date_end,
            },
        )

    else:
        return render(request, "phrase_analysis/phrase_analysis.html")
