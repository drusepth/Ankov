class Tentacle:

  # override
  def __init__(self):
    pass

  # override
  def start(self, config):
    pass

  def report(self, message):
    # todo default identifier
    print "[" + str(self.__class__.__name__) + ": " + str(self.identifier) + "] " + str(message)
