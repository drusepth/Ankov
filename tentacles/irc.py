# feels so java in here
import time
from random import random
import signal
import sys
import re
import os
import socket

import speech
import tentacle_base

#class IRC_Tentacle():
class IRC_Tentacle(tentacle_base.Tentacle):
  def __init__(self, config):
    self.irc_server   = config['server']
    self.irc_port     = config['port']
    self.irc_name     = 'ankov'
    self.irc_channels = config['channels']

    self.response_rate = 0.001     # % to respond to any line
    self.name_response_rate = 0.70 # % to respond to lines with bot's name
    self.response_length = 6       # has some wiggle room
    self.dictionary_req = 1000     # num words in dictionary before trying to respond

    self.markov = speech.Markov()
    try:
      self.markov.load("irc")
    except:
      self.markov.add_from_string("Hello")

    self.replied_to = []


  def start(self):
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect( (self.irc_server, self.irc_port) )
    irc.send(' '.join(['USER', self.irc_name, self.irc_name, self.irc_name, ':Ankov']) + "\n")
    irc.send(' '.join(['NICK', self.irc_name]) + "\n")
    con = irc.makefile('r', 0)

    while True:
      line = con.readline()

      if len(line) == 0:
        continue

      split = line.split(' ')

      if len(split) > 1 and split[0] == 'PING':
        irc.send(' '.join(['PONG', split[1]]) + "\r\n")
        continue

      if len(split) > 1 and (split[1] == '376' or split[1] == '422'):
        for channel in self.irc_channels:
          irc.send(' '.join(['JOIN', channel]) + "\n")
        continue

      if len(split) > 3 and split[1] == 'PRIVMSG':
        user    = split[0][1:] # dru!dru@host
        user    = user[0:user.find('!')] # dru
        channel = split[2]
        message = ' '.join(split[3:])[1:].rstrip()
        print('<' + user + '> ' + message)

        if (random() < self.response_rate or \
           (random() < self.name_response_rate and \
            message.find(self.irc_name) > -1)) and \
           channel.find('#') > -1 and \
           self.markov.word_size() > self.dictionary_req:

          try:
            response = self.markov.generate_markov_text(self.response_length + int(random() * 11) - 5)

            # Apply filters
            response = response.lower()
          
            if len(response) > 0:
              irc.send(' '.join(['PRIVMSG', channel, ':' + response]) + "\r\n")

          except KeyError:
            print('Caught some exception, go investigate')

        else: # Learn from IRC too!
          self.markov.add_from_string(message)

      self.markov.save("irc")
