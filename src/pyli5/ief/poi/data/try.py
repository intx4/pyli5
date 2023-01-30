from pyli5.ief.poi.watcher import Watcher
from queue import Queue
from os import path
import re
import time

class AMFGutiWatcher(Watcher):
    def __init__(self, log : str, q : Queue):
        super().__init__(q=q)
        self.re = "\[gmm\] [A-Z]{4,6}: \[([a-zA-F0-9-]{16,100})\]\s*5G-S_GUTI\[AMF_ID:(0x[0-9A-Fa-f]{5,6})\,M_TMSI:(0x[0-9A-Fa-f]{8})\]"
        f = open('amf.log')
        f.seek(path.getsize(f.name)) #EOF
        self.log = f

    def _watch(self):
        try:
            while True:
                lines = self.log.readlines()
                if lines:
                    for line in lines:
                        print("line: ", line)
                        m = re.search(self.re, line)
                        if m is not None:
                            suci, amf_id, tmsi = m.groups()
                            print(suci, amf_id, tmsi)
                time.sleep(1)
        except:
            self.log.close()


if __name__ == "__main__":
    w = AMFGutiWatcher("amf.log", Queue())
    w.watch()
    w.join()
