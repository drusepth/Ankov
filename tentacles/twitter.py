# feels so java in here
import time
from random import random
import tweetpony

import speech
from tentacle_base import Tentacle

class Twitter_Tentacle(Tentacle):
  def __init__(self, config):
    self.markov = speech.Markov()

    self.consumer_key = "6ilNIBBHz9ADYwFsaOgZw"
    self.consumer_secret = "0vajGMysk5d7UcttkJVilGEgJJVYXjffB7efagGxZs"
    self.access_token = "2273212922-JyXogbOzBN2pTFruX5XVc2lHalIn0nWLmxKPJWm"
    self.access_token_secret = "B3e90xXo3aNHHa83Ps2q68c4yksqitdJa7HtXF72SNzmc"

    self.api = tweetpony.API(consumer_key = self.consumer_key, \
                             consumer_secret = self.consumer_secret, \
                             access_token = self.access_token, \
                             access_token_secret = self.access_token_secret)
    self.identifier = '@' + self.api.user.screen_name

  def update_status(self, message):
    Tentacle.report(self, 'Updating status: ' + message)
    self.api.update_status(status = message)

  def start(self):
    Tentacle.report(self, 'Visiting the Twitters')

    self.api.update_status(status = 'hello world ' + str(random()))

    while True:
      results = self.api.search_tweets(q = 'cars')
      statuses = results['statuses']

      for status in statuses:
        print(status.text)
        humanized = self.markov.humanize_text(status.text)
        print(humanized)
        print("\n\n\n")

      time.sleep(120)

      #self.markov.add_from_string(message)
