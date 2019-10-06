# -*- coding: UTF-8 -*-

"""Download all videos from tweets containing a given hashtag, since a
specified date.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
import csv

import tweepy
import pandas as pd
import requests

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# Twitter API credentials
# (this won't work unless you have Twitter Developer access)
consumer_key=''
consumer_secret=''
access_token=''
access_token_secret=''

# hashtag to download videos of
hashtag = 'Iraq'

# starting date (i.e. download videos from tweets since this date)
start_date = "2019-10-04"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_video_url( tweet ):

  """If a tweet contains a video, return the video url.

  Parameters
  ----------
  tweet : tweepy.Status
    TweePy Status object containing information about a single tweet.

  Returns
  -------
  url : str or None
    If tweet contains a video, string of url of tht video.
    If tweet doesn't contain video, None.

  """

  try:
    url = tweet.extended_entities['media'][0]['video_info']['variants'][0]['url']
  except:
    url = None

  return url

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # create output directory of hashtag name if it doesn't exist already
  os.makedirs( hashtag, exist_ok = True )

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth,wait_on_rate_limit=True)

  # Open/Create a file to append data
  csvFile = open(f'{hashtag}.csv', 'a')
  #Use csv Writer
  csvWriter = csv.writer(csvFile)

  # initialize list of URLs; initializing with None so we don't have to worry
  # about downloading nonexistant video urls.
  urls_list = [None]

  # loop over all tweets since specified start_date and containing hashtag
  for tweet in tweepy.Cursor(
    api.search,
    q=hashtag,
    count=100,
    include_entities = True,
    since=start_date).items():

    # extract url from tweet, if it contains a video
    url = get_video_url( tweet )

    # check to make sure we haven't already downloaded the video for the given
    # url
    if url not in urls_list:
      urls_list.append( url )

      # video GET request
      r = requests.get( url )

      # printing status of request (should be 200 if nothing went wrong)
      print(r)

      # write video to file
      fname = os.path.join( hashtag, url.split('/')[-1] )
      with open(fname, 'wb') as f:
        f.write( r.content )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#