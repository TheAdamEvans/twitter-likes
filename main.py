import os
import re
from time import sleep
from datetime import datetime, timedelta
from dateutil.parser import parse

import twitter
from slackclient import SlackClient
from numpy.random import exponential


def is_yesterday(tweet, days = 1):
    tweet_time = parse(tweet.created_at).replace(tzinfo=None)
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

def create_msg(tweet):
    linkpattern = re.compile('https://t.co/[A-z0-9]+$')
    if linkpattern.match(tweet.text):
        msg = linkpattern.search(tweet.text).group(0)
    else:
        msg = tweet.user.screen_name.encode('utf8') + '\n' + tweet.text.encode('utf8')
    return msg

def main():
    # ping twitter for latest favorites
    api = twitter.Api(consumer_key = os.environ['TWITTER_CONSUMER_KEY'],
                      consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                      access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    favs = api.GetFavorites()
    
    # determine how long ago the tweet was favorited
    todays_favs = [f for f in favs if is_yesterday(f)]
    
    # extract text from the Status object
    msgs = map(create_msg, todays_favs)
    
    # send updates
    for msg in msgs:
        sleep(exponential(10))
        response = slack_msg(msg, '@adam.evans')
        print response

if __name__ == '__main__':
	main()
