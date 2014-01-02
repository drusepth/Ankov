# feels so java in here
import praw
import time
import random
import signal
import sys
import re
import os
import urllib2

import speech
from tentacle_base import Tentacle

class Reddit_Tentacle(Tentacle):
  def __init__(self, config):
    self.response_rate = 0.001 # %
    self.response_length = 12   # has some wiggle room
    self.dictionary_req = 5000 # num words in dictionary before trying to respond

    self.useragent = 'the internet beast by /u/drusepth'

    self.username = config['username']
    self.password = config['password']

    self.identifier = self.username

  def start(self):
    markov = speech.Markov()

    Tentacle.report(self, 'Logging in to Reddit')
    r = praw.Reddit(user_agent=self.useragent)
    r.login(self.username, self.password)
    Tentacle.report(self, 'logged in')

    replied_to = []

    while True:
      Tentacle.report(self, 'Searching for comments to reply to')
      subreddit = r.get_subreddit('all')

      for comment in subreddit.get_comments():
        responded = False
        if random.randint(0, self.response_rate * 10000) / 100 == 0 and \
           comment.id not in replied_to and \
           str(comment.author) != self.username and \
           markov.word_size() > self.dictionary_req and \
           not responded:

          try:
            response = markov.generate_markov_text(self.response_length + random.randint(-5, 5))

            if len(response) > 0:
              Tentacle.report(self, 'Responding with: ' + response)
              responded = True
              comment.reply(response)
              replied_to.append(comment.id)
              comment.upvote()
              time.sleep(30 + random.randint(30, 60))
            else:
              Tentacle.report(self, 'Not enough in cache to respond yet')

          except urllib2.HTTPError:
            Tentacle.report(self, 'Reddit is down omgomgomg')
            time.sleep(150 + random.randint(0, 400))

          except praw.errors.RateLimitExceeded:
            Tentacle.report(self, 'Rate limited')
            time.sleep(150 + random.randint(0, 500))

          except praw.errors.APIException:
            Tentacle.report(self, 'API Exception')
            time.sleep(150 + random.randint(0, 300))

        else: # not responding to them, so learn from them
          markov.add_from_string(comment.body)
          Tentacle.report(self, markov.word_size())

      Tentacle.report(self, 'Sleeping until later')
      time.sleep(300 + random.randint(300, 600))
