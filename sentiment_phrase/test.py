from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import preprocessing as p

f = open("Apr01.txt")
count = 0
analyzer = SentimentIntensityAnalyzer()
usernames = set()
location = set()
for line in f:
    if count < 2:
        vs = analyzer.polarity_scores(p.processAll(line.split("|")[-1]))
        if vs["compound"] < (-0.2):
            usernames.add(line.split("|")[3])
            location.add(line.split("|")[1])
print(location)
print(usernames)

# count=count+1
# print("hi")
