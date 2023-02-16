import json
import logging

from pyli5.iface.li_hiqr.li_hiqr import LI_HIQR
from pyli5.iface.li_hiqr.li_hiqr_server import HIQRPipe, H1_Q, HIQRMessage
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.utils.logger import Logger
from pyli5.admf.internal_iface import InternalInterface
from threading import Thread
from lxml import etree
from queue import Queue
class LICF:
    def __init__(self, li_iqf: InternalInterface, li_admf : InternalInterface):
        self.logger = Logger("LICF")
        self.li_admf = li_admf
        self.li_iqf = li_iqf
        self._arm()

    def _arm(self):
        t = Thread(daemon=True, target=self._dispatch_iqf_messages, args=())
        t.start()

    def _dispatch_iqf_messages(self):
        """ Receives notification from IQF and forwards to LIPF for activation of IEF if needed, then flags IQF when IEF is ready"""
        while True:
            req = self.li_iqf.get_request()
            self.logger.log("LI_IQF - LICF received request to activate IEF from IQF")
            self.li_admf.send_request(req)
            resp = self.li_admf.get_response()
            self.logger.log(f"LI_ADMF - LICF received response for activating IEF from LIPF. IEF Active = {resp}")
            self.li_iqf.send_response(resp)