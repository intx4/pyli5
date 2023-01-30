import json
import logging
import queue
import threading
import time
from dataclasses import dataclass
from multiprocessing import Process
from queue import Queue
from pyli5.iface.li_xem1.xem_server import XEMPipe, XEMServer, XEMMessage
from pyli5.ief.poi.amf_poi import AMFPoi
from pyli5.iface.li_xem1 import xem1
from pyli5.iface.li_xer.xer_client import XERClient
from pyli5.iface.x1.x1_messages import *
from pyli5.utils.logger import Logger
from pyli5.ief.ief_records import *
POOL = 1 #1s

class IEFBuffer():
    """
    IEFBuffer keeps track of the active user for this NEF
    """

    def __init__(self):
        self.buff = {}
        self._lock = threading.Lock()

    def store(self, supi: str, record: IEFAssociationRecord):
        self._lock.acquire()
        self.buff[supi] = record
        self._lock.release()
    def delete(self, supi: str):
        self._lock.acquire()
        if supi in self.buff.keys():
            self.buff.pop(supi)
        self._lock.release()
    def flush(self) -> [IEFAssociationRecord]:
        records = []
        self._lock.acquire()
        for k in self.buff.keys():
            records.append(self.buff[k])
        self.buff = {}
        self._lock.release()
        return records


class IEF():
    def __init__(self, config: str):
        with open(config, 'r') as f:
            c = json.load(f)
            self.ne_id = c['xem']["ne_id"]
            self.addr = c['xem']["ne_ip"]
            self.port = c['xem']["ne_port"]
            self.url = c['xem']["ne_url"]
            self.pool_interval = c['pool_interval']

            self.logger = Logger("IEF")

            self.task_lock = threading.Lock()
            self.Tasks = {}  # XID -> Task

            self.destination_lock = threading.Lock()
            self.Destinations = {}  # DID -> Destination

            self.xem = xem1.LI_XEM1(self.logger)
            self.xem_pipe = XEMPipe()
            self.xem.run_server(self.addr, self.port, self.url, self.xem_pipe)  # starts listening

            self.interception_q = IEFQ()
            self.poi = AMFPoi(c['poi']['log_watcher']['log'], self.interception_q, self.logger)

            self.buffer = IEFBuffer()
            self.active_lock = threading.Lock()
            self.active = False # reporting to ICF
        # !Activate
        self._arm()

    def is_active(self):
        self.active_lock.acquire()
        active = self.active
        self.active_lock.release()
        return active

    def activate(self):
        self.task_lock.acquire()
        self.destination_lock.acquire()
        self.active_lock.acquire()
        if len(self.Tasks.keys()) >= 1 and len(self.Destinations.keys()) >= 1 and not self.active:

            self.logger.log("IEF Activated and ready to report to ICF")
            self.active = True

        self.active_lock.release()
        self.destination_lock.release()
        self.task_lock.release()

    def _process_task(self, msg: X1Message) -> X1Message:
        self.logger.log(f" XEM1 - Received: {etree.tostring(msg.xml_encode(), pretty_print=True)}")
        self.task_lock.acquire()
        tasks = self.Tasks.keys()
        self.task_lock.release()
        if isinstance(msg.entity, ActivateTaskRequest):
            # new task
            if msg.entity.xId in tasks:
                # notify error
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=None,
                        error="XID already exists on NE",
                        code="2010",
                        type_for_error="ActivateTask",
                        type=TYPE_ERROR + "Response"
                    )
                )
                self.logger.log("XID already exists on NE", logging.ERROR)
            else:
                self.destination_lock.acquire()
                found = False
                for dId in msg.entity.dIds:
                    if dId in self.Destinations.keys():
                        found = True
                        break
                self.destination_lock.release()

                if not found:
                    resp = X1Message(
                        entity=SimpleResponse(
                            admf_id=msg.entity.admf_id,
                            ne_id=msg.entity.ne_id,
                            x1_transaction_id=msg.entity.x1_transaction_id,
                            ok=None,
                            error="No valid dId in request",
                            code="2010",
                            type_for_error="ActivateTask",
                            type=TYPE_ERROR + "Response"
                        )
                    )
                    self.logger.log("No valid dId in request", logging.ERROR)
                else:
                    self.task_lock.acquire()
                    self.Tasks[msg.entity.xId] = msg.entity
                    self.task_lock.release()
                    self.logger.log(f"Activated task XID={msg.entity.xId}")
                    resp = X1Message(
                        entity=SimpleResponse(
                            admf_id=msg.entity.admf_id,
                            ne_id=msg.entity.ne_id,
                            x1_transaction_id=msg.entity.x1_transaction_id,
                            ok=OK_ACKnCOMPLETED,
                            error=None,
                            code=None,
                            type_for_error=None,
                            type=TYPE_ACTIVATETASK + "Response"
                        )
                    )

                    self.activate()
                    if self.is_active():
                        buffered_events = self.buffer.flush()
                        self._report_ief_events(buffered_events)

        elif isinstance(msg.entity, DeactivateTaskRequest):
            # delete task
            if msg.entity.xId not in tasks:
                # notify error
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=None,
                        error="XID does not exist on NE",
                        code="2020",
                        type_for_error="DeActivateTask",
                        type=TYPE_ERROR + "Response"
                    )
                )
                self.logger.log(f"XID does not exist on NE", logging.ERROR)
            else:
                self.task_lock.acquire()
                self.Tasks.pop(msg.entity.xId)
                self.task_lock.release()
                self.logger.log(f"Removed task XID={msg.entity.xId}")

                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=OK_ACKnCOMPLETED,
                        error=None,
                        code=None,
                        type_for_error=None,
                        type=TYPE_DEACTIVATETASK + "Response"
                    )
                )
        return resp

    def _process_dest(self, msg: X1Message):
        self.logger.log(f"XEM1 - Received: {etree.tostring(msg.xml_encode(), pretty_print=True)}")
        self.destination_lock.acquire()
        destinations = self.Destinations.keys()
        self.destination_lock.release()

        if isinstance(msg.entity, CreateDestinationRequest):
            # new task
            if msg.entity.dId in destinations:
                # notify error
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=None,
                        error="DID already exists on NE",
                        code="2030",
                        type_for_error="CreateDestination",
                        type=TYPE_ERROR + "Response"
                    )
                )
                self.logger.log("DID already exists on NE", logging.ERROR)
            else:
                self.destination_lock.acquire()
                self.Destinations[msg.entity.dId] = msg.entity
                self.destination_lock.release()
                self.logger.log(f"Created Destination DID={msg.entity.dId}")
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=OK_ACKnCOMPLETED,
                        error=None,
                        code=None,
                        type_for_error=None,
                        type=TYPE_CREATEDESTINATION + "Response"
                    )
                )

                self.activate()
                if self.is_active():
                    buffered_events = self.buffer.flush()
                    self._report_ief_events(buffered_events)

        elif isinstance(msg.entity, RemoveDestinationRequest):
            # delete task
            if msg.entity.dId not in destinations:
                # notify error
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=None,
                        error="DID does not exist on NE",
                        code="2040",
                        type_for_error="RemoveDestination",
                        type=TYPE_ERROR + "Response"
                    )
                )
                self.logger.log(f"DID does not exist on NE", logging.ERROR)

            else:
                self.destination_lock.acquire()
                self.Destinations.pop(msg.entity.dId)
                self.destination_lock.release()
                self.logger.log(f"Removed destination DID={msg.entity.dId}")

                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=OK_ACKnCOMPLETED,
                        error=None,
                        code=None,
                        type_for_error=None,
                        type=TYPE_REMOVEDESTINATION + "Response"
                    )
                )
        return resp


    def _listen_xem(self):
        while True:
            msg = self.xem_pipe.get()
            if isinstance(msg.msg.entity, ActivateTaskRequest) or isinstance(msg.msg.entity, DeactivateTaskRequest):
                resp = self._process_task(msg.msg)
            elif isinstance(msg.msg.entity, CreateDestinationRequest) or isinstance(msg.msg.entity, RemoveDestinationRequest):
                resp = self._process_dest(msg.msg)
            else:
                # notify error
                resp = X1Message(
                    entity=SimpleResponse(
                        admf_id=msg.entity.admf_id,
                        ne_id=msg.entity.ne_id,
                        x1_transaction_id=msg.entity.x1_transaction_id,
                        ok=None,
                        error="X1 Message not supported",
                        code="1000",
                        type_for_error=msg.msg.entity.type.rstrip("Response").rstrip("Request"),
                        type=TYPE_ERROR + "Response"
                    )
                )
            msg.responseQ.put((200, etree.tostring(resp.xml_encode(), xml_declaration=True)))
            time.sleep(POOL)

    def _listen_poi(self):
        #start poi
        self.poi.intercept()
        while True:
            event = self.interception_q.get()

            # check if IEF has tasks, if not buff

            if self.is_active():
                # send over to destinations
                self.logger.log(f"Reporting received association event from POI: {event}")
                buffered_events = self.buffer.flush()
                buffered_events.append(event)
                self._report_ief_events(buffered_events)
            else:
                self.logger.log(f"Buffering received association event from POI: {event}")
                if event.assoc is not None:
                    self.buffer.store(event.assoc.supi, event)
                if event.deassoc is not None:
                    self.buffer.delete(event.deassoc.supi)

    def _report_ief_events(self, events:[IEFRecord]):
        # send over to destinations
        self.destination_lock.acquire()
        for did, dest in self.Destinations.items():
            host, port = dest.address, dest.port
            client = XERClient(self.logger)
            for e in events:
                client.send(host, port, e)
        self.destination_lock.release()

    def _arm(self):
        xem_listener = threading.Thread(daemon=True, target=self._listen_xem)
        xem_listener.start()
        poi_listener = threading.Thread(daemon=True, target=self._listen_poi)
        poi_listener.start()

