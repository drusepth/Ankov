import random
 
class Markov(object):

  def __init__(self):
    self.cache = {}
    self.words = []
    self.word_size = 0

  def add_from_string(self, string):
    self.words += string.split()
    self.word_size += len(string.split())
    self.database() # recalculate cache lolol

  def add_from_file(self, open_file):
    self.open_file = open_file
    self.words += self.file_to_words()
    self.word_size = len(self.words)
    self.database()

  def file_to_words(self):
    self.open_file.seek(0)
    data = self.open_file.read()
    words = data.split()
    return words

  """ Generates triples from the given data string. So if our string were
      "What a lovely day", we'd generate (What, a, lovely) and then
      (a, lovely, day).
  """
  def triples(self):
    if len(self.words) < 3:
      return
          
    for i in range(len(self.words) - 2):
      yield (self.words[i], self.words[i+1], self.words[i+2])
                 
  def database(self):
    for w1, w2, w3 in self.triples():
      key = (w1, w2)
      if key in self.cache:
        self.cache[key].append(w3)
      else:
        self.cache[key] = [w3]
                          
  def generate_markov_text(self, size=25):
    seed = random.randint(0, self.word_size - 3)
    seed_word, next_word = self.words[seed], self.words[seed + 1]
    w1, w2 = seed_word, next_word
    gen_words = []
    try:
      for i in xrange(size):
        gen_words.append(w1)
        w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w2)
    except KeyError: # not enough in cache to form valid chain
      gen_words = []

    return ' '.join(gen_words)
