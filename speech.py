import random
import pickle
import os
import re

from itertools import chain

# For this graph, you can assume "parents" are all words that come prior
# to a node's value in a sentence, and "children" are all words that can
# come afterwards.
class Node:
  def __init__(self, value, parent):
    self.parents  = [parent]
    self.children = []
    self.value    = value
    self.weight   = 1 # todo implement frequency weights

  def add_child(self, child):
    if child not in self.children:
      self.children.append(child)

  def add_parent(self, parent):
    if parent not in self.parents:
      self.parents.append(parent)

class Markov(object):

  # Initialize the markov generator object
  def __init__(self):
    self.graph = {}
    self.graph['<<START>>'] = Node('<<START>>', None)
    self.ngram = 4 # size of ngrams

  # Serialize self into memory/bank_name
  def save(self, bank_name):
    path = 'memory/' + str(bank_name)
    existing_graph = {}

    # Load the on-disk graph into our live one to prevent clobbering changes
    if os.path.exists(path):
      with open(path) as deserialize:
        existing_graph = pickle.load(deserialize)

    # Merge the two graphs together into a new one
    # todo merge children/parents rather than just key->value
    self.graph = dict(chain(existing_graph.items(), self.graph.items()))

    # Save the combined graph to disk
    with open(path, 'w+') as serialize:
      pickle.dump(self.graph, serialize)

  # Deserialize memory/bank_name into self
  def load(self, bank_name):
    path = 'memory/' + str(bank_name)
    if os.path.exists(path):
      with open(path) as serialize:
        self.graph = pickle.load(serialize)

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
      consequent = words[index + self.ngram - 1]

      print(antecedent + " --> " + consequent)

      # If the antecedent ("There is...") is not in the graph yet, quickly add it
      if antecedent not in self.graph.keys():
        self.graph[antecedent] = Node(antecedent, None)

      # Because ngram size can be >1, go ahead and reverse-index the antecedent
      # to point to the previous word, too
      if index != 0:
        #print("adding " + words[index - 1] + " <-- " + antecedent)
        self.graph[antecedent].add_parent(words[index - 1])

      # If the consequent already exists in the graph, give it an additional parent
      if consequent in self.graph.keys():
        self.graph[consequent].add_parent(antecedent)

        # (And give its parent an additional child)
        self.graph[antecedent].add_child(consequent)

      else:
        # If the consequent does not already exist in the graph, add it to the graph
        # and assign it as a child to its parent.
        self.graph[consequent] = Node(consequent, antecedent)
        self.graph[antecedent].add_child(consequent)

  # Open a file and feed it into the graph
  def add_from_file(self, filename):
    path = 'memory/' + str(filename)
    if os.path.exists(path):
      with open(path) as open_file:
        contents = open_file.seek(0).read()
        return self.add_from_string(contents)

  # Returns how many words are in the vocabulary
  def word_size(self):
    return len(self.graph)

  # Generate markov chain
  def generate_markov_text(self, size=25, starter=None):
    current_word = starter

    # If the starter word isn't known, pick a random one instead
    if starter is None or current_word.split()[0] not in self.graph.keys():
      keys = self.graph.keys()
      current_word = keys[random.randint(0, len(keys) - 1)]
      starter = current_word

    text = [current_word]

    #print("staring with " + current_word)

    # Begin building the string to the left, until we hit a <<START>> token.
    # To avoid continuously prepending to an array, we're going to append to
    # one and then reverse it all at once afterwards.
    while current_word != None and current_word in self.graph.keys() and len(text) <= size:
      # Fetch a list of all parents
      if len(self.graph[current_word].parents) > 1:
        # Disallow None parents if there are any other potential parents
        parents = [x for x in self.graph[current_word].parents if x is not None]
      else:
        parents = self.graph[current_word].parents

      #print("parents:")
      #print(parents)

      # Choose one at random, and step to it. Because everything except our
      # start token should have a parent, we're going to forgo a check here
      # and assume len(parents) > 0.
      parent = parents[random.randint(0, len(parents) - 1)]
      if parent != None:
        text.append(parent)
      current_word = parent

      #print("chose:")
      #print(parent)

    # After we finally reach a start token, go ahead and reverse the array
    # to put the words in the correct order, before moving on to the second
    # half of the sentence to generate.
    text.reverse()

    #print("message progress at mid: ")
    #print(text)

    current_word = starter
    #print("starting back at mid: " + current_word)
    #while len(self.graph[current_word].children) > 0:
    while current_word != '<<END>>' and len(text) <= size:
      # If this child doesn't have any children (possible with large ngram sizes),
      # attempt to rectify the situation by pulling in previous words
      max_depth = self.ngram
      while max_depth > 0:
        max_depth -= 1

        # If children are possible, ignore everything
        if current_word in self.graph.keys() and len(self.graph[current_word].children) > 0:
          break

        # Because nodes in text can consist of multiple words (when ngram size > 1)
        # rejoin and resplit on each expansion iteration.
        text = ' '.join(text).split()
        #print("text is ")
        #print(text)

        # If there are no more words to expand, don't try to absorb more
        if len(current_word.split()) >= len(text):
          print('not enough words to absorb')
          break

        current_word = ' '.join([text[-2], current_word])
        
        if current_word in self.graph.keys():
          children = self.graph[current_word].children
          #print("expanding current_word to " + current_word)

          # If adding the word prefix now introduces children, break out early
          if len(self.graph[current_word].children) > 0:
            break

      # If it's impossible to move forward in the sentence from here, break early
      if current_word not in self.graph.keys() or len(self.graph[current_word].children) == 0:
        break

      # Fetch a list of all possible children
      children = self.graph[current_word].children

      # Choose one randomly and step in
      child = children[random.randint(0, len(children) - 1)]
      #print("chose child: " + child)

      # Because a child might have been expanded, only take the last word of it to append
      text.append(child.split()[-1])
      current_word = child

    #print('generated')
    #print(text)

    # Before joining text fragments, we want to filter out our tokens
    tokens = ['<<START>>', '<<END>>']
    text = ' '.join([x for x in text if x is not None]).split()
    string = ' '.join([x for x in text if x not in tokens]) # todo combine these two lines?

    return self.humanize_text(string)

  # Run a string through some filters meant to make it look more human-written
  def humanize_text(self, string):
    #print('Humanizing ' + string)

    # Remove all URLs
    string = re.sub(r'https?:\/\/[^\s]*', '', string, flags=re.MULTILINE)

    # Remove reddit-style links remaining (i.e.: "[link text](" )
    # todo

    # Make sure all quotes are closed
    if string.count('"') % 2 == 1:
      string = string + '"'

    # Strip out <username>: message, replies (esp. for IRC)
    if string.find(':') < string.find(' '):
      string = string[string.index(' ')+1:]

    # Capitalize the first letter after every period
    sentences = string.split('.')
    sentences = map((lambda letter: letter.strip().capitalize()), sentences)
    print(sentences)
    string = '. '.join(sentences)

    # And at the risk of copypasting code, also capitalize after question marks
    sentences = string.split('?')
    sentences = map((lambda letter: letter.strip().capitalize()), sentences)
    print(sentences)
    string = '? '.join(sentences)

    # Capitalize all lonely instances of i
    string = string.replace(" i ", " I ")

    # Replace remnant . . . from above spliit with ...
    string = string.replace(". . .", "...")

    print('Humanized: ' + string)

    return string
