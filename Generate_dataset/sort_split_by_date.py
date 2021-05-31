from datetime import datetime
import os
import random


def getparams(time_str):
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
    month = months[time_str[4:7]]
    date = int(time_str[8:10])
    hour = int(time_str[11:13])
    minute = int(time_str[14:16])
    second = int(time_str[17:19])
    timestamp = datetime(2017, month, date, hour, minute, second).timestamp()
    return timestamp


file = open("organized_tweets.txt")
contents = file.readlines()
timestamp_tweet = {}
count = 0
for row in contents:
    print(count)
    timestamp = getparams(row.split("|")[0])
    timestamp_tweet[timestamp] = row
    count += 1

timestamps_keys = list(timestamp_tweet.keys())
timestamps_keys.sort()
sorted_tweets = []
for key in timestamps_keys:
    sorted_tweets.append(timestamp_tweet[key])

month_date = ""
index_file = open("../index.txt", "w")

root_dir = "../Dataset3/"

try:
    os.system("rm -rf ../Dataset3/")
    os.mkdir("../Dataset3/")
except:
    pass

for row in sorted_tweets:
    if row.split("|")[0][4:10] != month_date:
        month_date = row.split("|")[0][4:10]
        file.close()
        filename = (
            "../Dataset3/" + row.split("|")[0][4:7] + row.split("|")[0][8:10] + ".txt"
        )
        file = open(filename, "w")
        index_file.write(row.split("|")[0][4:7] + row.split("|")[0][8:10] + "\n")
        file.write(row)
    else:
        file.write(row)


for filename in os.listdir(root_dir):
    file = open(root_dir + filename)
    file_contents = file.readlines()
    file.close()
    length = len(file_contents)
    count = 0
    if length > 10000:
        file = open(root_dir + filename, "w")
        for row in file_contents:
            if random.random() <= 10000 / length:
                count += 1
                file.write(row)
        file.close()
    print(filename + ": ", length, count)
