# feels so java in here
import praw
import time
import random
import signal
import sys
import re
import os

import speech
import tentacle_base

class Reddit_Tentacle(tentacle_base.Tentacle):
  def __init__(self, config):
    self.response_rate = 0.001 # %
    self.response_length = 6   # has some wiggle room
    self.dictionary_req = 2000 # num words in dictionary before trying to respond

    self.useragent = 'the internet beast by /u/drusepth'

    self.username = config['username']
    self.password = config['password']

  def start(self):
    print('Building starter markov dictionary')
    markov = speech.Markov()
    try:
      markov.load("reddit")
    except:
      markov.add_from_string("Hello")
    print('Good to go')

    print('Logging in to Reddit')
    r = praw.Reddit(user_agent=self.useragent)
    r.login(self.username, self.password)
    print('logged in')

    replied_to = []

    while True:
      print('Searching for comments to reply to')
      subreddit = r.get_subreddit('all')

      for comment in subreddit.get_comments():
        if random.randint(0, self.response_rate * 10000) / 100 == 0 and \
           comment.id not in replied_to and \
           str(comment.author) != self.username and \
           markov.word_size() > self.dictionary_req:

          try:
            response = markov.generate_markov_text(self.response_length + random.randint(-5, 5))

            # Apply some filters to humanize the text
            response = response.lower()
            #response = re.sub("[\.\:;\(\)\"\*]", "", response, 0, 0)

            if len(response) > 0:
              print('Responding')
              comment.reply(response)
              replied_to.append(comment.id)
              comment.upvote()
              time.sleep(300 + random.randint(150, 300))
            else:
              print('Not enough in cache to respond yet')

          except praw.errors.RateLimitExceeded:
            print('Rate limited')
            time.sleep(150 + random.randint(0, 500))
            pass

          except praw.errors.APIException:
            print('API Exception')
            time.sleep(150 + random.randint(0, 300))
            pass

        else: # not responding to them, so learn from them
          markov.add_from_string(comment.body)
          print(markov.word_size())

      print('Done looking through comments, saving dictionary')
      markov.save("reddit")

      print('And sleeping until later')
      time.sleep(300 + random.randint(300, 600))
