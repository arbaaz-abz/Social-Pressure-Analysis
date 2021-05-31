from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import re

# Hashtags
hash_regex = re.compile(r"#(\w+)")


def hash_repl(match):
    return "" + match.group(1)


# Handels
hndl_regex = re.compile(r"@(\w+)")


def hndl_repl(match):
    return ""  # _'+match.group(1).upper()


# URLs
url_regex = re.compile(r"(http|https|ftp)://[a-zA-Z0-9\./]+")

# Spliting by word boundaries
word_bound_regex = re.compile(r"\W+")

# Repeating words like hurrrryyyyyy
rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE)


def rpt_repl(match):
    # return ''
    return match.group(1) + match.group(1)


# negation words
negate = [
    "aint",
    "arent",
    "cannot",
    "cant",
    "couldnt",
    "darent",
    "didnt",
    "doesnt",
    "ain't",
    "aren't",
    "can't",
    "couldn't",
    "daren't",
    "didn't",
    "doesn't",
    "dont",
    "hadnt",
    "hasnt",
    "havent",
    "isnt",
    "mightnt",
    "mustnt",
    "neither",
    "don't",
    "hadn't",
    "hasn't",
    "haven't",
    "isn't",
    "mightn't",
    "mustn't",
    "neednt",
    "needn't",
    "never",
    "none",
    "nope",
    "nor",
    "not",
    "nothing",
    "nowhere",
    "oughtnt",
    "shant",
    "shouldnt",
    "uhuh",
    "wasnt",
    "werent",
    "oughtn't",
    "shan't",
    "shouldn't",
    "uh-uh",
    "wasn't",
    "weren't",
    "without",
    "wont",
    "wouldnt",
    "won't",
    "wouldn't",
    "rarely",
    "seldom",
    "despite",
    "would not",
    "could not",
    "has not",
    "had not",
    "have not",
    "are not",
    "is not",
    "am not",
    "will not",
    "shall not",
    "ought not",
    "should not",
    "did not",
    "does not",
    "do not",
    "dare not",
    "might not ",
    "must not ",
    "need not ",
    "can not ",
    "was not ",
    "were not ",
    "lack of",
    "noo",
]

# Emoticons
emoticons = [
    ("__emot_smiley", [":-)", ":)", "(:", "(-:", "B)", "B-)"]),
    (
        "__emot_laugh",
        [
            ":-D",
            ":D",
            "X-D",
            "XD",
            "xD",
        ],
    ),
    ("__emot_love", ["<3", "<3<3", "<<3"]),
    (
        "__emot_wink",
        [
            ";-)",
            ";)",
            ";-D",
            ";D",
            "(;",
            "(-;",
        ],
    ),
    ("__emot_frown", [":-(", ":(", "(:", "(-:", ":/"]),
    ("__emot_cry", [":,(", ":'(", ':"(', ":(("]),
]

# Punctuations
punctuations = [
    (
        "__punc_excl",
        [
            "!",
            "¡",
        ],
    ),
    (
        "__punc_ques",
        [
            "?",
            "¿",
        ],
    ),
    (
        "__punc_ellp",
        [
            "...",
            "…",
        ],
    ),
    (
        "__punc_more",
        ["{", "}", "[", "]", ":", ";", ",", "-"],
    ),  # FIXME : MORE? http://en.wikipedia.org/wiki/Punctuation
]

# Printing functions for info
def print_config(cfg):
    for (x, arr) in cfg:
        print(x, "\t")
        for a in arr:
            print(a, "\t")
        print("")


def print_emoticons():
    print_config(emoticons)


def print_punctuations():
    print_config(punctuations)


# For emoticon regexes
def escape_paren(arr):
    return [text.replace(")", "[)}\]]").replace("(", "[({\[]") for text in arr]


def regex_union(arr):
    return "(" + "|".join(arr) + ")"


emoticons_regex = [
    (repl, re.compile(regex_union(escape_paren(regx)))) for (repl, regx) in emoticons
]

# For punctuation replacement
def punctuations_repl(match):
    text = match.group(0)
    repl = []
    for (key, parr) in punctuations:
        for punc in parr:
            if punc in text:
                repl.append(key)
    if len(repl) > 0:
        return " " + " ".join(repl) + " "
    else:
        return " "


def processHashtags(text, subject="", query=[]):
    return re.sub(hash_regex, hash_repl, text)


def processHandles(text, subject="", query=[]):
    return re.sub(hndl_regex, hndl_repl, text)


def processUrls(text, subject="", query=[]):
    return re.sub(url_regex, " __url ", text)


def processEmoticons(text, subject="", query=[]):
    for (repl, regx) in emoticons_regex:
        text = re.sub(regx, " " + repl + " ", text)
    return text


def processPunctuations(text, subject="", query=[]):
    print("punc\n")
    return re.sub(word_bound_regex, punctuations_repl, text)


def processRepeatings(text, subject="", query=[]):
    print("repeat\n")
    return re.sub(rpt_regex, rpt_repl, text)


def processQueryTerm(text, subject="", query=[]):
    query_regex = "|".join([re.escape(q) for q in query])
    return re.sub(query_regex, "__quer", text, flags=re.IGNORECASE)


def findNegations(text):
    # Bigram
    for word in negate:
        if word in text:
            # print("FOUND : ",word)
            text = text.replace(word, "__negation")
            # print(text)
    return text


def processAll(text, subject="", query=[]):
    arr = []
    text = re.sub(hash_regex, hash_repl, text)
    text = re.sub(hndl_regex, hndl_repl, text)
    text = re.sub(url_regex, "", text)
    for (repl, regx) in emoticons_regex:
        text = re.sub(regx, " " + "" + " ", text)
    text = " ".join(re.findall(r"[\w']+|[!.,'-]", text))
    # print(text)
    # text = re.sub( word_bound_regex , punctuations_repl, text )
    text = re.sub(rpt_regex, rpt_repl, text)
    # text = findNegations(text)
    return text


analyzer = SentimentIntensityAnalyzer()
total = 0
count = 0
points = []
for i in range(3, 12):
    if i < 10:
        a = "kkk_jul_0" + str(i)
    else:
        a = "kkk_jul_" + str(i)
    m = a + ".txt"
    f = open(m)
    for line in f:
        sentence_split = line.split("|", 4)
        tweet = sentence_split[-1]
        process_tweet = processAll(tweet)
        vs = analyzer.polarity_scores(tweet)
        total = total + vs["compound"]
        count = count + 1
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
