import json
import sys
import os
from pyli5.lea.lea import LEA
from pyli5.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger("Bootstrapper")
    logger.log("Starting application")
    with open(os.environ["HOME"]+"/pyli5/src/pyli5/lea/client.json") as f:
        logger.debug("Read from config file")
        c = json.load(f)
        lea = LEA(id=c['id'],
                  hiqr_addr=c['hiqr_addr'], hiqr_port=c['hiqr_port'],
                  iqf_addr=c['iqf_addr'], iqf_port=c['iqf_port'],
                  grpc_port=c['grpc_port'])
        logger.log("LEA started")

    # this is for running a local test for grpc client side
    #
    #lea = LEA(id="1",
    #              hiqr_addr="127.0.0.1", hiqr_port="12344",
    #              iqf_addr="127.0.0.1", iqf_port="12345",
    #              grpc_port="48888")
    while True:
        pass
