import sys
from pyli5.ief.ief import IEF
import os
from pyli5.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger("Bootstrapper")
    ief = IEF(config=os.environ["HOME"]+"/pyli5/src/pyli5/ief/ief.json")
    logger.log("IEF started")
    while True:
        pass
