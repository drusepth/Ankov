from threading import Thread

import tentacles.irc as irc
import tentacles.reddit as reddit

reddit = Thread(target=reddit.start) #,args=({})
reddit.daemon = True
reddit.start()

intern = Thread(target=irc.start)
intern.daemon = True
intern.start()

try:
  while True:
    pass
except KeyboardInterrupt:
  print('Killing the monster')
