import signal
import sys
import time

from threading import Thread

import tentacles.reddit as reddit

reddit = Thread(target=reddit.start) #,args=({})
reddit.start()
reddit.join()
