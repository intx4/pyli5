import sys
import os
from pyli5.catcher.catcher import Catcher
from pyli5.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger("Bootstrapper")
    catcher = Catcher(path=os.environ["HOME"]+"/pyli5/src/pyli5/catcher/catcher.json")
    logger.log("Catcher started")
    while True:
        pass
