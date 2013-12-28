from threading import Thread

from tentacles.irc import IRC_Tentacle
from tentacles.reddit import Reddit_Tentacle

tentacles = []

irc_vectors = [
  {
    'server': 'irc.amazdong.com',
    'port':   6667,
    'channels': [
      '#ankov'
    ]
  },
]

reddit_vectors = [
  {
    'username': 'aniravigali',
    'password': 'e269201c4f025659de7072f73fb4c433'
  },
  {
    'username': 'japlandian',
    'password': '6f2f01539468a88f60877828b0312b04'
  }
]

# Spawn IRC tentacles
for vector in irc_vectors:
  tentacle = IRC_Tentacle(vector)
  t = Thread(target = tentacle.start)
  t.daemon = True
  tentacles.append(t)
  t.start()

# Spawn reddit tentacles
for vector in reddit_vectors:
  tentacle = Reddit_Tentacle(vector)
  t = Thread(target = tentacle.start)
  t.daemon = True
  tentacles.append(t)
  t.start()

try:
  while True:
    pass
except KeyboardInterrupt:
  print('Killing the monster')
