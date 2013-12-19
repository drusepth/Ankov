from threading import Thread

import tentacles.reddit as reddit

reddit = Thread(target=reddit.start) #,args=({})
reddit.daemon = True
reddit.start()

try:
  while True:
    pass
except KeyboardInterrupt:
  print('Killing the monster')
