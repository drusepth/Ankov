from threading import Thread

from tentacles.irc import IRC_Tentacle
import tentacles.reddit as reddit

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

for vector in irc_vectors:
  tentacle = IRC_Tentacle(vector)
  t = Thread(target = tentacle.start)
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
