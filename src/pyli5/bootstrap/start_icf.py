import json
import sys
import os
sys.path.append(os.environ["HOME"]+"/p3li5/pyli5/src/")
from pyli5.icf import ICF

if __name__ == "__main__":
    with open(os.environ["HOME"]+"/p3li5/pyli5/src/pyli5/icf/server.json") as f:
        c = json.load(f)
        icf = ICF(xqr_addr=c['xqr_addr'], xqr_port=c['xqr_port'], grpc_port=c['grpc_port'])
    while True:
        pass
