# For this graph, you can assume "parents" are all words that come prior
# to a node's value in a sentence, and "children" are all words that can
# come afterwards.
class Redis:
  def __init__(self):
    import redis
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

