from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

analyzer = SentimentIntensityAnalyzer()
f = input().split()
total = 0
count = 0
phrase = input()
length = int(f[1])
points = []
for i in range(4, length):
    if i < 10:
        a = "Aug_0" + str(i)
    else:
        a = "Aug_" + str(i)
    m = a + ".txt"
    file = open(m)
    for sentence in file:
        if phrase in sentence:
            vs = analyzer.polarity_scores(sentence)
            total = total + vs["compound"]
            count = count + 1
    if count == 0:
        continue
    res = total / count
    print(res)
    points.append(res)
x = [int(i) for i in range(1, len(points) + 1)]
y = points
print(x)
print(y)
plt.plot(x, y)
plt.title("Sentiment Analysis Report")
plt.xlabel("Days")
plt.ylabel("Sentiment Value")
plt.show()
