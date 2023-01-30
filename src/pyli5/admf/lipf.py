import json

from pyli5.iface.li_xem1.xem1 import LI_XEM1
from pyli5.iface.li_xem1.xem_server import *
from pyli5.iface.x1.x1 import *
from pyli5.iface.x1.x1_messages import *
from pyli5.utils.logger import Logger
from threading import Thread
from lxml import etree
from queue import Queue
from pyli5.utils.identifiers import gen_random_uuid
from dataclasses import dataclass

@dataclass
class ICFInfo():
    xer_addr : str
    xer_port : str

@dataclass
class IEFInfo():
    xem_addr: str
    xem_port: str
    xem_url: str
    xem_id : str


class IEFStatus:
    def __init__(self):
        self.tasks = {}
        self.known_destinations = {}

class LIPF:
    def __init__(self, admf_id, icf_info: ICFInfo, ief_info: IEFInfo, li_admf : Queue()):
        self.logger = Logger("LIPF")
        self.admf_id = admf_id
        self.li_admf = li_admf

        self.ief_status = IEFStatus()
        self.ief_info = ief_info

        self.icf_info = icf_info

        self.xem = LI_XEM1(self.logger)
        self._arm()

    def _arm(self):
        t = Thread(daemon=True, target=self._dispatch_li_admf_messages, args=())
        t.start()

    def _dispatch_li_admf_messages(self):
        while True:
            msg = self.li_admf.get(block=True)
            header = msg["Header"]
            warrant = msg["Warrant"]
            self.logger.log(f"LI_ADMF - Received warrant: LEA {etree.tostring(header.xml_encode())} DOCUMENT REFERENCE {warrant.doc_ref}")

            if len(self.ief_status.known_destinations.keys()) == 0:
                x1_tx_id = gen_random_uuid()
                dId = gen_random_uuid()
                self.ief_status.known_destinations[dId] = True
                dst_msg = X1Message(CreateDestinationRequest(self.admf_id, self.ief_info.xem_id, x1_tx_id, dId, self.icf_info.xer_addr,self.icf_info.xer_port))
                self.xem.send(self.ief_info.xem_addr, self.ief_info.xem_port, self.ief_info.xem_url, dst_msg)

            x1_tx_id = gen_random_uuid()
            xId = gen_random_uuid()
            self.ief_status.tasks[xId] = True
            task_msg = X1Message(ActivateTaskRequest(self.admf_id, self.ief_info.xem_id, x1_tx_id, xId, self.ief_status.known_destinations.keys()))
            self.xem.send(self.ief_info.xem_addr, int(self.ief_info.xem_port), self.ief_info.xem_url, task_msg)