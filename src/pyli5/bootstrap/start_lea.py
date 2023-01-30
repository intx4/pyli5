import json
import sys
import os
sys.path.append(os.environ["HOME"]+"/p3li5/pyli5/src/")
from pyli5.lea import LEA

if __name__ == "__main__":
    with open(os.environ["HOME"]+"/p3li5/pyli5/src/pyli5/lea/client.json") as f:
        c = json.load(f)
        lea = LEA(id=c['id'],
                  hiqr_addr=c['hiqr_addr'], hiqr_port=c['hiqr_port'],
                  iqf_addr=c['iqf_addr'], iqf_port=c['iqf_port'],
                  grpc_port=c['grpc_port'])
    while True:
        pass
