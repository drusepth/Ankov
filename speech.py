import random
import pickle
import os

# For this graph, you can assume "parents" are all words that come prior
# to a node's value in a sentence, and "children" are all words that can
# come afterwards.
class Node:
  def __init__(self, value, parent):
    self.parents  = [parent]
    self.children = []
    self.value    = value
    self.weight   = 1 # todo implement frequency weight

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
    self.graph["<<START>>"] = Node("<<START>>", None)

  # Serialize self into memory/bank_name
  def save(self, bank_name):
    with open('memory/' + bank_name, 'w+') as serialize:
      pickle.dump(self.graph, serialize)

  # Deserialize memory/bank_name into self
  def load(self, bank_name):
    path = 'memory/' + str(bank_name)
    if os.path.exists(path):
      with open(path) as serialize:
        self.graph = pickle.load(serialize)

  # Break string down into ngrams and add them to the graph
  def add_from_string(self, string):
    previous_word = "<<START>>"
    for word in string.split():
      if word in self.graph.keys():
        # If this word already exists in the graph, give it an additional parent
        self.graph[word].add_parent(previous_word)          

        # (And give its parent an additional child)
        self.graph[previous_word].add_child(word)

      else:
        # If this word does not already exist in the graph, add it to the graph
        # and assign it as a child to its parent.
        self.graph[word] = Node(word, previous_word)
        self.graph[previous_word].add_child(word)

      # After adding children and parents, update the previous_word
      previous_word = word

    # After looping through all the words, link the last word to <<END>>
    self.graph[previous_word].add_child("<<END>>")

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
  def generate_markov_text(self, size=25, starter="<<START>>"):
    current_word = starter
    text = [current_word]

    # Begin building the string to the left, until we hit a <<START>> token.
    # To avoid continuously prepending to an array, we're going to append to
    # one and then reverse it all at once afterwards.
    while current_word != "<<START>>":
      # Fetch a list of all parents 
      parents = self.graph[current_word].parents

      # Choose one at random, and step to it. Because everything except our
      # start token should have a parent, we're going to forgo a check here
      # and assume len(parents) > 0.
      parent = parents[random.randint(0, len(parents) - 1)]
      text.append(parent)
      current_word = parent

    # After we finally reach a start token, go ahead and reverse the array
    # to put the words in the correct order, before moving on to the second
    # half of the sentence to generate.
    text.reverse()

    current_word = starter
    while current_word != "<<END>>":
      # Fetch a list of all children
      children = self.graph[current_word].children

      # Choose a child at random, step to it.
      child = children[random.randint(0, len(children) - 1)]
      text.append(child)
      current_word = child

    # Sentence should now span from <<START>> to <<END>>, with actual stuff
    # inside. Strip out the first and last node (tokens), and return the
    # generated sentence.
    text.pop(0)  # <<START>>
    text.pop(-1) # <<END>>

    return ' '.join(text)
