import csv, re

# Extract tweets and sentiments from the original train dataset
dataset = "immigration_tweets.csv"
write_tweets = "organized_tweets.txt"
handle_tweets = open(write_tweets, "w")
i = 1
with open(dataset, "r") as f:
    handle = csv.reader(f)
    for line in handle:
        if line[10] == "en" or line[10] == "und":
            print("tweet : ", i)
            created_at = str(line[1]).strip(" ")
            user_location = str(line[27]).split(",")
            user_location = " ".join(user_location)
            user_location = user_location.strip(" ")
            user_location = re.sub(r"\n", "", user_location)

            user_name = str(line[28]).strip(" ")
            user_name = re.sub(r"\n", "", user_name)

            user_screen_name = str(line[29]).strip(" ")
            user_screen_name = re.sub(r"\n", "", user_screen_name)

            tweet = line[17].strip(" ")
            tweet = " ".join(tweet.split())
            tweet = re.sub(r"\n", "", tweet)

            row = (
                created_at.strip("\n")
                + "|"
                + user_location.strip("\n")
                + "|"
                + user_name.strip("\n")
                + "|"
                + user_screen_name.strip("\n")
                + "|"
                + tweet.strip("\n")
                + "\n"
            )
            handle_tweets.write(row)
            i += 1
print("Done extracting tweets")
handle_tweets.close()
