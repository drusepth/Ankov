import random
import pickle
import redis
import re

from itertools import chain

# For this graph, you can assume "parents" are all words that come prior
# to a node's value in a sentence, and "children" are all words that can
# come afterwards.
class Redis:
  def __init__(self):
    self.connection = redis.StrictRedis()
    # todo introduce cache, set each key on get, expire that key on set

  def add_antecedent(self, key, antecedent):
    key = str(key) + '_antecedents'
    self.connection.sadd(key, antecedent)

  def add_consequent(self, key, consequent):
    key = str(key) + '_consequents'
    self.connection.sadd(key, consequent)

  def get_antecedents(self, key):
    key = str(key) + '_antecedents'
    return self.connection.smembers(key)

  def get_consequents(self, key):
    key = str(key) + '_consequents'
    return self.connection.smembers(key)

  def keys(self):
    return self.connection.keys()

  def random_key(self):
    preparsed = self.connection.randomkey()

    # remove _antecedents and _consequents
    if preparsed.find('_') > -1:
      preparsed = '_'.join(preparsed.split('_')[:-1])

    return preparsed

class Markov(object):
  # Initialize the markov generator object
  def __init__(self):
    self.ngram = 4 # max size of ngrams

    self.redis = Redis()

  # Break string down into ngrams and add them to the graph
  def add_from_string(self, string):
    words = string.split()
    words.insert(0, "<<START>>")
    words.append("<<END>>")

    if len(words) < self.ngram:
      return

    for index in range(0, len(words) - self.ngram + 1):
      # Build ngram antecedents for variable ngram size
      antecedents = []
      for i in range(0, self.ngram - 1):
        antecedents.append(words[index + i])

        antecedent = ' '.join(antecedents)
        consequent = words[index + i + 1]

        #print(antecedent + " --> " + consequent)

        # Because ngram size can be >1, go ahead and reverse-index the antecedent
        # to point to the previous word, too
        if index != 0:
          #print(words[index - 1] + " <-- " + antecedent)
          self.redis.add_antecedent(antecedent, words[index - 1])

        # Add consequent index -- and the reverse
        self.redis.add_consequent(antecedent, consequent)
        self.redis.add_antecedent(consequent, antecedent)

  # Open a file and feed it into the graph
  def add_from_file(self, filename):
    path = 'memory/' + str(filename)
    if os.path.exists(path):
      with open(path) as open_file:
        contents = open_file.seek(0).read()
        return self.add_from_string(contents)

  # Returns how many words are in the vocabulary
  def word_size(self):
    return len(self.redis.keys())

  # Generate markov chain
  def generate_markov_text(self, size=25, starter=None):
    current_word = starter

    # If the starter word isn't known, pick a random one instead
    if len(self.redis.get_consequents(starter)) == 0:
      current_word = self.redis.random_key()
      starter = current_word

    text = [current_word]

    #print("staring with " + current_word)

    # Begin building the string to the left, until we hit a <<START>> token.
    # To avoid continuously prepending to an array, we're going to append to
    # one and then reverse it all at once afterwards.

    while current_word != '<<START>>' and \
          len(self.redis.get_antecedents(current_word)) > 0 and \
          len(text) <= size:

      # Fetch a list of all parents
      antecedents = self.redis.get_antecedents(current_word)

      # No known antecedents, move on
      if len(antecedents) == 0:
        break

      # Choose one at random, and step to it. Because everything except our
      # start token should have a parent, we're going to forgo a check here
      # and assume len(parents) > 0.
      antecedent = random.sample(antecedents, 1)[0]
      text.append(antecedent)
      current_word = antecedent

      # todo need to absorb words going forward too

      #print("chose:")
      #print(antecedent)

    # After we finally reach a start token, go ahead and reverse the array
    # to put the words in the correct order, before moving on to the second
    # half of the sentence to generate.
    text.reverse()

    #print("message progress at mid: ")
    #print(text)

    #print(starter)
    current_word = starter
    #print("starting back at mid: " + current_word)
    #while len(self.graph[current_word].children) > 0:
    while current_word != '<<END>>' and len(text) <= size:
      # If this child doesn't have any children (possible with large ngram sizes),
      # attempt to rectify the situation by pulling in previous words
      max_depth = self.ngram
      absorbtion_index = -2 # index of word to absorb, increases as we absorb
      while max_depth > 0:
        max_depth -= 1

        # If children are possible, ignore everything
        if len(self.redis.get_consequents(current_word)) > 0:
          break

        # Because nodes in text can consist of multiple words (when ngram size > 1)
        # rejoin and resplit on each expansion iteration.
        text = ' '.join(text).split()
        #print("text is ")
        #print(text)

        #print('current_word is')
        #print(current_word)

        # If there are no more words to expand, don't try to absorb more
        if len(current_word.split()) >= len(text):
          print('not enough words to absorb')
          break

        current_word = ' '.join([text[absorbtion_index], current_word])
        #print('after set, current_word is ' + current_word)
        absorbtion_index -= 1

      #print("out of absorbtion loop")

      # If it's impossible to move forward in the sentence from here, break early
      if len(self.redis.get_consequents(current_word)) == 0:
        break

      # Fetch a list of all possible children
      children = self.redis.get_consequents(current_word)
      #print("children are ")
      #print(children)

      # Choose one randomly and step in
      child = random.sample(children, 1)
      #print("chose child: ")
      #print(child)

      # Because a child might have been expanded, only take the last word of it to append
      text.append(child[0].split()[-1])
      current_word = child[0]

    #print('generated')
    #print(text)

    # Before joining text fragments, we want to filter out our tokens
    tokens = ['<<START>>', '<<END>>']
    #print(text)
    string = ' '.join([x for x in ' '.join(text).split() if x not in tokens])

    #print('humanizing ' + string)
    return self.humanize_text(string)

  # Run a string through some filters meant to make it look more human-written
  def humanize_text(self, string):
    #print('Humanizing ' + string)

    # Normalize text to lowercase before performing translations
    string = string.lower()

    # Remove all URLs
    string = re.sub(r'https?:\/\/[^\s]*', '', string, flags=re.MULTILINE)

    # Remove reddit-style links remaining (i.e.: "[link text](" )
    # todo

    # Make sure all quotes are closed
    if string.count('"') % 2 == 1:
      string = string + '"'

    # Strip out <username>: message, replies (esp. for IRC)
    if string.find(':') > -1 and string.find(':') < string.find(' '):
      string = string[string.find(' ')+1:]

    # Strip out @name and @name: replies, (esp. for twitter)
    if len(string) > 0 and string[0] == '@':
      string = string[string.find(' ')+1:]

    # Strip out RT @Name: prefixes
    string = re.sub(r'(?:^|\s)rt @[^\s]* ', '', string, flags=re.MULTILINE)

    # Strip out a final via @name
    string = re.sub(r'via @[^\s]*$', '', string, flags=re.MULTILINE)

    # Strip out all hashtags
    string = re.sub(r'#[^\s]*', '', string, flags=re.MULTILINE)

    # Capitalize the first letter after every period
    sentences = string.split('. ')
    if len(sentences) > 1:
      sentences = map((lambda letter: letter.strip().capitalize()), sentences)
      string = '. '.join(sentences)

    # And at the risk of copypasting code, also capitalize after question marks
    sentences = string.split('? ')
    if len(sentences) > 1:
      sentences = map((lambda letter: letter.strip().capitalize()), sentences)
      string = '? '.join(sentences)

    # ...and exclamation points
    sentences = string.split('! ')
    if len(sentences) > 1:
      sentences = map((lambda letter: letter.strip().capitalize()), sentences)
      string = '! '.join(sentences)

    # Capitalize all lonely instances of i
    string = string.replace(" i ", " I ")

    # Replace &amp; with & because wow
    string = string.replace('&amp;', '&')

    # Replace remnant . . . from above spliit with ...
    string = string.replace(". . .", "...")

    # If the last character is a comma or some other punctuation, remove it
    if string[-1] in [',', ':', '-', '@']:
      string = ''.join(list(string)[:-1])

    #print('Humanized: ' + string)

    return string
