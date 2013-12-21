from threading import Thread

import tentacles.irc as irc
import tentacles.reddit as reddit

tentacles = []

irc_vectors = [
  {
    'server': 'irc.amazdong.com',
    'port':   6667,
    'channels': [
      '#interns',
      '#ankov'
    ]
  },
  {
    'server': 'irc.tddirc.net',
    'port':   6667,
    'channels': [
      '#hackerthreads'
    ]
  }
]

for vector in irc_vectors:
  t = Thread(target=irc.start, args=([vector]))
  t.daemon = True
  tentacles.append(t)
  t.start()

reddit = Thread(target=reddit.start) #,args=({})
reddit.daemon = True
reddit.start()

try:
  while True:
    pass
except KeyboardInterrupt:
  print('Killing the monster')
