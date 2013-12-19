import praw
import time
import random

import markovgen
import settings

response_rate = 0.001
response_length = 6
dictionary_req = 1000 # num words in dictionary before trying to respond

print('Building starter markov dictionary')
markov = markovgen.Markov()
file_ = open('corpus/empty.txt')
markov.add_from_file(file_)
print('Good to go')

print('Logging in to Reddit')
r = praw.Reddit(user_agent=settings.useragent())
r.login(settings.username(), settings.password())
print('logged in')

replied_to = []

while True:
  print('Searching for comments to reply to')
  subreddit = r.get_subreddit('all')

  for comment in subreddit.get_comments():
    if random.randint(0, response_rate * 10000) / 100 == 0 and \
       comment.id not in replied_to and \
       str(comment.author) != settings.username() and \
       markov.word_size > dictionary_req:

      try:
        response = markov.generate_markov_text(response_length + random.randint(-5, 5))
        if len(response) > 0:

          print('Responding')

          comment.reply(response)
          replied_to.append(comment.id)
          comment.upvote()
          time.sleep(90 + random.randint(0, 30))
        else:
          print('Not enough in cache to respond yet')

      except praw.errors.RateLimitExceeded:
        print('Rate limited')
        time.sleep(150 + random.randint(0, 150))
        pass

      except praw.errors.APIException:
        print('API Exception')
        time.sleep(120 + random.randint(0, 90))
        pass

    else: # not responding to them, so learn from them
      markov.add_from_string(comment.body)
      print(markov.word_size)

  print('Done looking through comments, sleeping')
  time.sleep(300 + random.randint(0, 60))
