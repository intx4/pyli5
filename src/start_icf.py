import json
import sys
import os
from pyli5.icf.icf import ICF
from pyli5.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger("Bootstrapper")
    logger.log("Starting application")
    with open(os.environ["HOME"]+"/pyli5/src/pyli5/icf/server.json") as f:
        logger.debug("Read from config file")
        c = json.load(f)
        icf = ICF(xqr_addr=c['xqr_addr'], xqr_port=c['xqr_port'], grpc_port=c['grpc_port'])
        logger.log("ICF started")
    while True:
        pass
