import tweepy
import json
import textblob
import re
import pandas as pd
with open('credentials.json', 'r') as f:
    cred = json.load(f)
    
consumer_key = cred['api_key']
consumer_secret = cred['api_key_secret']
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

def byUsername():
    user_name = input("Enter Username : ")
    user = api.get_user(user_name)
    timeline = api.user_timeline(user.id, tweet_mode = "extended")
    return timeline

def byQueries():
    query = input("Enter search query : ")
    num = input("Enter number of tweets : ")
    searched_tweets = api.search(q = query, count = num)
    ids = []
    for tweet in searched_tweets:
        ids.append(tweet.id)
    tweets = []
    for tweet_id in ids:
        tweets.append(api.get_status(tweet_id, tweet_mode = "extended"))
    return tweets

def get_tweet_data(tweets):
    header = ['id', 'author', 'full_text', 'retweet_count', 'favorite_count', 'Polarity']
    tweets_data = []
    for tweet in tweets:
        status_dict = vars(tweet)
        tweet_data = {}
        for key in status_dict.keys():
            if key in header:
                if key == 'author':
                    tweet_data[key] = status_dict[key].screen_name
                elif key == 'full_text':
                    text = status_dict[key].replace("\u2019", "'")
                    tweet_data[key] = text
                else:
                    tweet_data[key] = status_dict[key]
        tweets_data.append(tweet_data)
    return tweets_data

def get_hashtags(tweet):
    text = tweet['full_text']
    pattern = re.compile(r"#(\w+)")
    hashtags = re.findall(pattern, text)
    return hashtags

def get_polarity(tweet):
    text = tweet['full_text']
    clean_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())
    analysis = textblob.TextBlob(clean_text)
    return analysis.sentiment.polarity

def get_dataframe(data):
    col = ['id', 'author', 'full_text', 'hashtag(s)', 'retweet_count', 'favorite_count', 'Polarity']
    df = pd.DataFrame(data = data, columns = col)
    return df

while True:
    print("1. Get tweet data by username")
    print("2. Get tweet data by query")
    print("3. Exit")
    choice = input("Enter Choice : ")
    if choice != '1' and (choice != '2' and choice != '3'):
        print("Invalid Choice...\n_________________________________________________________________\n")
        continue
    elif choice == '3':
        break
    elif choice == '1':
        data = get_tweet_data(byUsername())
    elif choice == '2':
        data = get_tweet_data(byQueries())

    for tweet in data:
        tweet['Polarity'] = get_polarity(tweet)
        tweet['hashtag(s)'] = get_hashtags(tweet)
        
    dataframe = get_dataframe(data)
    print(dataframe)
    
    choice2 = input("Data fetched..\nDo you want to save the data(Y/N) : ")
    if choice2.lower() == 'y':
        file_name = input("Enter file name : ")
        dataframe.to_csv(file_name +'.csv')
        with open(file_name + '.json', 'w') as f:
           f.write(json.dumps(data, indent = 4))
        print("Data added to the file...")
    
    print("_________________________________________________________________\n")
