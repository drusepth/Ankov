from threading import Thread

from tentacles.irc import IRC_Tentacle
from tentacles.reddit import Reddit_Tentacle
from tentacles.twitter import Twitter_Tentacle

tentacles = []

irc_vectors = [
  {
    'server': 'irc.amazdong.com',
    'port':   6667,
    'channels': [
      '#ankov',
      '#interns'
    ]
  },
  {
    'server': 'irc.freenode.net',
    'port':   6667,
    'channels': [
      '#c', '##linux', '##overflow', '#freenode', '#perl', '#python', '#ruby', '#ubuntu',
      '#c#', '#archlinux', '#bitcoin', '#debian', '#haskell', '#gentoo', '#node.js',
      '#redis'
    ]
  },
  {
    'server': 'irc.tddirc.net',
    'port':   6667,
    'channels': [
      '#thunked', '#hackerthreads', '#shells', '#corecraft'
    ]
  }
]

reddit_vectors = [
  {
    'username': 'aniravigali',
    'password': 'e269201c4f025659de7072f73fb4c433'
  },
  {
    'username': 'oprahversiontwo',
    'password': 'a1cb02bf6d240de3338e72b5f0d3f268'
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

# Spawn twitter tentacles
tentacle = Twitter_Tentacle({})
t = Thread(target = tentacle.start)
t.daemon = True
t.start()

try:
  while True:
    pass
except KeyboardInterrupt:
  print('Killing the monster')
