import logging
import queue
import string
import time
import json
import re
from datetime import datetime
from queue import Queue, Empty
from os import path
from threading import Thread
import sys
from pyli5.utils.logger import Logger
from pyli5.utils.identifiers import tmsi_to_hex
from pyli5.utils.time import get_time_no_ms
import string
import requests
from dataclasses import dataclass

@dataclass
class Interception:
    type : str
    value : str

class InterceptionQ():
    def __init__(self):
        self.q = Queue(maxsize=0)

    def put(self, c : Interception):
        self.q.put(c)

    def get(self,timeout=0.0)->Interception:
        return self.q.get(block=True, timeout=timeout)

class LogWatcher():
    """
    Observers ueransim nr_ue.log file to find registration events
    This is compatible with https://github.com/intx4/ueransimLI

    :param path : str - path to log file
    :q : IEFQ - for sending ief assoc/deassoc events to poi logic
    :shut_down : - queue[bool] for triggering shutdown of interception
    """
    CATCHER_RE = r"CATCHER -- IDENTITY TYPE \[([A-Z]{4})\] VALUE \[(.*)\]"
    def __init__(self, path : str, q : InterceptionQ, logger : Logger):
        self.log = path
        self.logger = logger
        self.q = q

    def watch(self):
        f = open(self.log)
        try:
            #f.seek(path.getsize(f.name))  # go to EOF
            log = f
            while True:
                line = log.readline()
                if line:
                    m = re.search(LogWatcher.CATCHER_RE, line)
                    if m is not None:
                        typ, value = m.groups()
                        interception = Interception(type=typ, value=value)
                        if typ == "TMSI":
                            value = tmsi_to_hex(value)
                        self.logger.log(f" CATCHER - new association event {typ}={value}")
                        self.q.put(c=interception)
                else:
                    continue
        except Exception as ex:
            self.logger.error(f"CATCHER - panic {str(ex)}")
            log.close()

class Catcher():
    """
    :param config: json config file
    :param iefQ queue for passing interception products to the ief logic to be sent to ICF
    :param shut_down : queue for receiving shutdown signal from ief to stop interception
    """
    def __init__(self, path: str):
        self.q = InterceptionQ()
        with open(path,'r') as f:
            c = json.load(f)
            self.logger = Logger("CATCHER")
            self.watcher = LogWatcher(c['log_path'], self.q, self.logger)
            self.buffer = []
            self._relay(c['lea_ip'],c["lea_interception_port"],c["lea_interception_url"])

    def _relay(self, ip, port, url):
        watcher = Thread(daemon=True, target=self.watcher.watch)
        watcher.start()
        while True:
            time.sleep(0.1)
            try:
                interception = self.q.get(timeout=1)
                timestamp = get_time_no_ms()
                payload = json.dumps({"type": interception.type, "value": interception.value, "timestamp": timestamp})
                l = str(len(payload))
                try:
                    response = requests.post(url=f"http://{ip}:{port}{url}", data=payload,
                                  headers={"Content-Length": l, 'Content-Type': 'application/json'})
                    self.logger.log(f"CATCHER - Sending {payload} to http://{ip}:{port}{url}")
                    self.logger.log(f"CATCHER - Response: {response.status_code} - {response.content.decode()}")
                except Exception as ex:
                    self.logger.error(f"CATCHER - Error {str(ex)}")
                    self.logger.log(f"CATCHER - Buffering {payload}")
                    self.buffer.append(payload)
            finally:
                while len(self.buffer) > 0:
                    time.sleep(0.1)
                    payload = self.buffer[0]
                    l = str(len(payload))
                    try:
                        response = requests.post(url=f"http://{ip}:{port}{url}", data=payload,
                              headers={"Content-Length": l, 'Content-Type': 'application/json'})
                        self.logger.log(f"CATCHER - Sending {payload} to http://{ip}:{port}{url}")
                        self.logger.log(f"CATCHER - Response: {response.status_code} - {response.content.decode()}")
                        self.buffer = self.buffer[1:]
                    except:
                        break
                continue


