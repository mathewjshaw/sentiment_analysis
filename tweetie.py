import sys

import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tweepy

def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items
def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret,access_token, access_token_secret = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:
       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()
    Return a dictionary containing keys-value pairs:
       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary
    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    user_dictionary = dict()
    tweets = []
    vader = SentimentIntensityAnalyzer()
    public_tweets = api.user_timeline(screen_name = name, count = 100)

    for t in public_tweets:
        tweet_dictionary = dict()
        tweet_dictionary['id'] = t.id
        tweet_dictionary['created'] = t.created_at.date()
        tweet_dictionary['retweeted'] = t.retweet_count
        tweet_dictionary['text'] = t.text
        tweet_dictionary['hashtags'] = [h.replace('#', '') for h in t.text.replace('\n',' ').split(" ") if h.startswith("#")]
        tweet_dictionary['urls'] = [u for u in t.text.split(" ") if u.startswith("http")]
        tweet_dictionary['mentions'] = [h.replace('@', '') for h in t.text.replace('\n',' ').split(" ") if h.startswith("@")]
        tweet_dictionary['score'] = vader.polarity_scores(t.text)['compound']
        tweets.append(tweet_dictionary)

    user_dictionary['user'] = name
    user_dictionary['count'] = api.get_user(name).statuses_count
    user_dictionary['tweets'] = tweets

    return user_dictionary


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:
       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image
    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    followed_list = []
    followers = api.friends_ids(screen_name = name, count = 100)

    for id in followers:
        f = api.get_user(id = id)
        follower_dictionary = dict()

        follower_dictionary['name'] = f.name
        follower_dictionary['screen_name'] = f.screen_name
        follower_dictionary['followers'] = f.followers_count
        follower_dictionary['created'] = f.created_at.date()
        follower_dictionary['image'] = f.profile_image_url
        followed_list.append(follower_dictionary)

    sorted_followed_list = sorted(followed_list, key = lambda k: k['followers'], reverse = True)

    return sorted_followed_list



"""
TESTING
api = authenticate('twitter.csv')
fetch_tweets(api, '@realDonaldTrump')
fetch_following(api, '@realDonaldTrump')
"""
