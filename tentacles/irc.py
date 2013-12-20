# feels so java in here
import praw
import time
from random import random
import signal
import sys
import re
import os
import socket

#sys.path.insert(0, '../') #lol

import markovgen

response_rate = 0.001     # % to respond to any line
name_response_rate = 0.70 # % to respond to lines with bot's name
response_length = 6       # has some wiggle room
dictionary_req = 1000     # num words in dictionary before trying to respond

irc_server = 'irc.amazdong.com'
irc_port = 6667
irc_name = 'ankov'
irc_channel = '#interns'

def start():
  #todo share this across all tentacles
  print('Building starter markov dictionary')
  markov = markovgen.Markov()
  try:
    markov.load("irc")
  except:
    markov.add_from_string("Hello")
  print('Good to go')

  print('Logging in to IRC')
  irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  irc.connect( (irc_server, irc_port) )
  irc.send(' '.join(['USER', irc_name, irc_name, irc_name, ':Ankov']) + "\n")
  irc.send(' '.join(['NICK', irc_name]) + "\n")
  con = irc.makefile('r', 0)
  print('logged in')

  replied_to = []

  print('Starting IRC loop')
  while True:
    line = con.readline()
    split = line.split(' ')
    #print(line)
    #print(split)

    if len(split) > 1 and split[0] == 'PING':
      irc.send(' '.join(['PONG', split[1]]) + "\r\n")
      continue

    if len(split) > 1 and (split[1] == '376' or split[1] == '422'):
      irc.send(' '.join(['JOIN', irc_channel]) + "\n")
      continue

    if len(split) > 3 and split[1] == 'PRIVMSG':
      user    = split[0][1:] # dru!dru@host
      user    = user[0:user.find('!')] # dru
      channel = split[2]
      message = ' '.join(split[3:])[1:].rstrip()
      print('<' + user + '> ' + message)

      if (random() < response_rate or \
         (random() < name_response_rate and \
          message.find(irc_name) > -1)) and \
         channel.find('#') > -1 and \
         markov.word_size > dictionary_req:

        try:
          response = markov.generate_markov_text(response_length + int(random() * 11) - 5)

          # Apply filters
          response = response.lower()
          
          if len(response) > 0:
            print('Responding')
            irc.send(' '.join(['PRIVMSG', channel, ':' + response]) + "\r\n")
        except KeyError:
          print('Caught some exception, go investigate')

      else: # Learn from IRC too!
        markov.add_from_string(message)

    markov.save("irc")
