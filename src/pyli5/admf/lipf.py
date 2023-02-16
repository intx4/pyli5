import json
from pyli5.iface.li_xem1.xem1 import LI_XEM1
from pyli5.iface.li_xem1.xem_server import *
from pyli5.iface.x1.x1 import *
from pyli5.iface.x1.x1_messages import *
from pyli5.iface.x1.x1_xml import *
from pyli5.utils.logger import Logger
from pyli5.admf.internal_iface import InternalInterface
from threading import Thread, Lock
from lxml import etree
from queue import Queue
from pyli5.utils.identifiers import gen_random_uuid
from dataclasses import dataclass

@dataclass
class ICFInfo():
    xer_addr : str
    xer_port : str
    dId : str = None

@dataclass
class IEFInfo():
    xem_addr: str
    xem_port: str
    xem_url: str
    xem_id : str


class IEFStatus:
    def __init__(self):
        self.lock = Lock()
        self.active = False
        self.dest_knowledge = False

    def activate(self):
        with self.lock:
            self.active = True

    def add_destination_knowledge(self):
        with self.lock:
            self.dest_knowledge = True

    def knows_destination(self):
        with self.lock:
            return self.dest_knowledge
    def is_active(self):
        with self.lock:
            return self.active and self.dest_knowledge
class LIPF:
    def __init__(self, admf_id, icf_info: ICFInfo, ief_info: IEFInfo, li_admf : InternalInterface):
        self.logger = Logger("LIPF")
        self.admf_id = admf_id
        self.li_admf = li_admf

        self.ief_status = IEFStatus()

        self.ief_info = ief_info
        icf_info.dId = gen_random_uuid()
        self.icf_info = icf_info

        self.xem = LI_XEM1(self.logger)
        self._arm()

    def _arm(self):
        t = Thread(daemon=True, target=self._dispatch_li_admf_messages, args=())
        t.start()

    def _dispatch_li_admf_messages(self):
        dId = self.icf_info.dId
        while True:
            req = self.li_admf.get_request()
            self.logger.log(f"LI_ADMF - LIPF Received request to activate IEF")

            if self.ief_status.is_active():
                self.logger.log(f"LIPF - IEF already active")
                self.li_admf.send_response(True)
                continue

            if not self.ief_status.knows_destination():
                self.logger.log(f"LIPF - Creating Destination for IEF")
                try:
                    x1_tx_id = gen_random_uuid()
                    dst_msg = X1Message(CreateDestinationRequest(self.admf_id, self.ief_info.xem_id, x1_tx_id, dId, self.icf_info.xer_addr,self.icf_info.xer_port))
                    resp = self.xem.send(self.ief_info.xem_addr, self.ief_info.xem_port, self.ief_info.xem_url, dst_msg)
                    if resp.error is not None:
                        self.logger.error(f"LIPF - failed to add destination to IEF, got TopLevelErrorResponse (bad XML request)")
                        self.li_admf.send_response(False)
                        continue
                    else:
                        if resp.entity.error is not None:
                            self.logger.error(f"LIPF - failed to add destination to IEF: {resp.entity.error}")
                            self.li_admf.send_response(False)
                            continue
                        else:
                            self.ief_status.add_destination_knowledge()
                            self.logger.log(f"LIPF - added destination to IEF: {resp.entity.ok}")
                except Exception as ex:
                    self.logger.error(f"LIPF - failed to add destination to IEF: {str(ex)}")
                    self.li_admf.send_response(False)
                    continue
                finally:
                    self.logger.log(f"LIPF - Activating Task for IEF")
                    try:
                        x1_tx_id = gen_random_uuid()
                        xId = gen_random_uuid()
                        task_msg = X1Message(ActivateTaskRequest(self.admf_id, self.ief_info.xem_id, x1_tx_id, xId, [dId]))
                        resp = self.xem.send(self.ief_info.xem_addr, int(self.ief_info.xem_port), self.ief_info.xem_url, task_msg)
                        if resp.error is not None:
                            self.logger.error(
                                f"LIPF - failed to add task to IEF, got TopLevelErrorResponse (bad XML request)")
                            self.li_admf.send_response(False)
                            continue
                        else:
                            if resp.entity.error is not None:
                                self.logger.error(f"LIPF - failed to add task to IEF: {resp.entity.error}")
                                self.li_admf.send_response(False)
                                continue
                            else:
                                self.ief_status.activate()
                                self.logger.log(f"LIPF - added task to IEF: {resp.entity.ok}")
                    except Exception as ex:
                        self.logger.error(f"LIPF - failed to add task to IEF: {str(ex)}")
                        self.li_admf.send_response(False)
                        continue
                    finally:
                        self.logger.log(f"LIPF - IEF Status: {self.ief_status.is_active()}")
                        self.li_admf.send_response(self.ief_status.is_active())
                        continue
            elif not self.ief_status.is_active():
                self.logger.log(f"LIPF - Activating Task for IEF")
                try:
                    x1_tx_id = gen_random_uuid()
                    xId = gen_random_uuid()
                    task_msg = X1Message(ActivateTaskRequest(self.admf_id, self.ief_info.xem_id, x1_tx_id, xId, [dId]))
                    resp = self.xem.send(self.ief_info.xem_addr, int(self.ief_info.xem_port), self.ief_info.xem_url,
                                         task_msg)
                    if resp.error is not None:
                        self.logger.error(
                            f"LIPF - failed to add task to IEF, got TopLevelErrorResponse (bad XML request)")
                        self.li_admf.send_response(False)
                        continue
                    else:
                        if resp.entity.error is not None:
                            self.logger.error(f"LIPF - failed to add task to IEF: {resp.entity.error}")
                            self.li_admf.send_response(False)
                            continue
                        else:
                            self.ief_status.activate()
                            self.logger.log(f"LIPF - added task to IEF: {resp.entity.ok}")
                except Exception as ex:
                    self.logger.error(f"LIPF - failed to add task to IEF: {str(ex)}")
                    self.li_admf.send_response(False)
                    continue
                finally:
                    self.logger.log(f"LIPF - IEF Status: {self.ief_status.is_active()}")
                    self.li_admf.send_response(self.ief_status.is_active())
                    continue
            self.logger.log(f"LIPF - IEF Status: {self.ief_status.is_active()}")
            self.li_admf.send_response(self.ief_status.is_active())

#if __name__ == "__main__":
#
#    li_admf = InternalInterface()
#    lipf = LIPF("1", None, None, li_admf)
#    li_admf.send_request(True)
#    while True:
#        pass