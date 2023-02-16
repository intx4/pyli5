import logging
from logging import *
from pathlib import Path
import os
from threading import Lock

MAXLEN = 64*1024
def _create_dir(path):
    is_exist = os.path.exists(path)
    if not is_exist:
        # Create a new directory because it does not exist
        os.makedirs(path)

LOG_PATH = str(Path.home())+"/pyli5/var/log"

_create_dir(str(Path.home())+"/pyli5")
_create_dir(str(Path.home())+"/pyli5/var")
_create_dir(str(Path.home())+"/pyli5/var/log")

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
class Logger():
    def __init__(self, name : str, path = LOG_PATH):
        handler = logging.FileHandler(path+"/"+name+".log")
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        self.l = logger
        self._lock = Lock()
    def log(self, msg:str):
        self._lock.acquire()
        self.l.info(msg)
        self._lock.release()

    def debug(self, msg:str):
        self._lock.acquire()
        self.l.debug(msg)
        self._lock.release()

    def error(self, msg:str):
        self._lock.acquire()
        self.l.error(msg)
        self._lock.release()

    def warn(self, msg:str):
        self._lock.acquire()
        self.l.warn(msg)
        self._lock.release()