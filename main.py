from numpy.random import exponential
from time import sleep

from datetime import datetime, timedelta
from dateutil.parser import parse

import os
from slackclient import SlackClient
import re

import twitter

def is_yesterday(f, days = 1):
    tweet_time = parse(f.created_at).replace(tzinfo=None)
    tweet_age = datetime.utcnow() - tweet_time
    return tweet_age < timedelta(days)


def slack_msg(msg, channel):
    sc = SlackClient(os.environ["SLACK_API_TOKEN"])
    return sc.api_call(
        "chat.postMessage",
        channel=channel,
        username='twitter-likes',
        as_user = True,
        text=msg
    )

def create_msg(f):
    linkpattern = re.compile('https://t.co/[A-z0-9]+$')
    if linkpattern.match(f.text):
        msg = linkpattern.search(f.text).group(0)
    else:
        msg = f.user.screen_name.encode('utf8') + '\n' + f.text.encode('utf8')
    return msg

def main():
    # ping twitter for latest favorites
    api = twitter.Api(consumer_key = os.environ['TWITTER_CONSUMER_KEY'],
                      consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                      access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    fav = api.GetFavorites()
    
    # determine how long ago the tweet was favorited
    todays_favs = [f for f in fav if is_yesterday(f)]
    
    # extract text from the Status object
    tweets = map(create_msg, todays_favs)
    
    # send updates
    for t in tweets:
        sleep(exponential(10))
        response = slack_msg(t, '@adam.evans')
        print response

if __name__ == '__main__':
	main()
