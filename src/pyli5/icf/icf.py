"""
from typing import Dict, List

from pyli5.iface.li_xer.xer_server import run_server
from pyli5.ief.ief import IEFQ, IEFRecord, IEFDeassociationRecord, IEFAssociationRecord
import json
import threading as T
from datetime import datetime
import time
from multiprocessing import Process

class CacheRecord():
    def __init__(self, event : IEFAssociationRecord):
        self.supi = event.supi
        self.guti = event.fivegguti
        self.suci = event.suci
        self.timestamp = event.timestmp
        self.ncgi = event.ncgi
        self.ncgi_time = event.ncgi_time
        self.pei = event.pei
        self.tai = event.tai
        self.list_of_tai = event.list_of_tai

        self.assoc_time = self.timestamp
        self.deassoc_time = ""

    def record_deassoc_time(self, deassoc_time):
        self.deassoc_time = deassoc_time
        

class CacheEntry():
    def __init__(self, record : CacheRecord):
        self.current = record
        self.current_bd = time.time()
        self.previous = None #tbd: supporting > 2 records at a time
        self.previous_bd = None

    def _copy_record(self, target : CacheRecord, source : CacheRecord):
        target.supi = source.supi
        target.guti = source.guti
        target.suci = source.suci
        target.timestamp = source.timestamp
        target.ncgi = source.ncgi
        target.ncgi_time = source.ncgi_time

        #retain pei if no new one is available
        if source.pei is not None or source.pei != "":
            target.pei = source.pei

        #retain list of tai if no new one
        if source.list_of_tai is not None:
            if len(source.list_of_tai) != 0:
                target.list_of_tai = source.list_of_tai

        target.tai = source.tai

        target.assoc_time = source.timestamp
        target.deassoc_time = target.deassoc_time
    def new_association(self, record: CacheRecord):
        # Currently active association is marked as previously active, and new one is registered as current
        self._copy_record(self.previous, self.current)
        self.previous.record_deassoc_time(record.timestamp)
        self.previous_bd = self.current_bd
        self.current = record
        self.current_bd = time.time()

    def deassociate(self, event: IEFDeassociationRecord):
        #IEFDeassociation event is received : currently active is marked as deassociated
        if self.current.guti == event.fivegguti:
            self._copy_record(self.previous, self.current)
            self.previous.record_deassoc_time(event.timestmp)
            self.current = None
            self.current_bd = None
        elif self.previous.guti == event.fivegguti:
            self.previous.record_deassoc_time(event.timestmp)


class Cache():
    def __init__(self, cache_ttl, max_ttl):
        self._cache_ttl = cache_ttl
        self._max_ttl = max_ttl
        self._storage = Dict[str, CacheEntry]
        self._lock = T.Lock()
        self._guti_lock = T.Lock()
        self._guti_lut = Dict[str, List[str]]
        self._suci_lock = T.Lock()
        self._suci_lut = Dict[str, List[str]]


        self._caching_daemon()

    def _caching_func(self):
        while True:
            with self._lock.acquire():
                marked_to_delete = []
                clock = time.time()
                for k, record in self._storage.items():
                    if record.previous is not None and record.previous_bd is not None:
                        if clock-record.previous_bd >= self._cache_ttl:
                            record.previous = None
                            record.previous_bd = None
                    if record.current is not None and record.current_bd is not None:
                        if clock-record.current_bd >= self._max_ttl:
                            record.current = None
                            record.current_bd = None
                    if record.current is None and record.previous is None:
                        marked_to_delete.append(k)
                for k in marked_to_delete:
                    self._storage.pop(k)
            time.sleep(self._cache_ttl)

    def _caching_daemon(self):
        t = T.Thread(daemon=True, target=self._caching_func)
        t.start()

    def store_event_by_supi(self, event : IEFRecord):
        with self._lock.acquire():
            if event.assoc is not None:
                record = CacheRecord(event.assoc)
                if record.supi in self._storage.keys():
                    entry = self._storage.get(record.supi)
                    entry.new_association(record)
                else:
                    self._storage.update({record.supi:CacheEntry(record)})
            elif event.deassoc is not None:
                if event.deassoc.supi in self._storage.keys():
                    self._storage.get(event.deassoc.supi).deassociate(event.deassoc)

    def store_event_by_guti(self, event : IEFRecord):
        with self._lock.acquire():
            if event.assoc is not None:
                record = CacheRecord(event.assoc)
                if record.guti in self._storage.keys():
                    entry = self._storage.get(record.guti)
                    entry.new_association(record)
                else:
                    self._storage.update({record.guti:CacheEntry(record)})
            elif event.deassoc is not None:
                if event.deassoc.fivegguti in self._storage.keys():
                    self._storage.get(event.deassoc.fivegguti).deassociate(event.deassoc)

    def store_event_by_suci(self, event : IEFRecord):
        with self._lock.acquire():
            if event.assoc is not None:
                record = CacheRecord(event.assoc)
                if record.suci in self._storage.keys():
                    entry = self._storage.get(record.suci)
                    entry.new_association(record)
                else:
                    self._storage.update({record.suci:CacheEntry(record)})

class ICF(Process):
    
    #ICF is the caching component for registering identity associations events
    #It receives new association events from IEF(s) via the LI_XER interface
    #It receives queries for identity associations via the LI_XQR interface
    

    def __init__(self, config):
        super(ICF, self).__init__(target=self._init)
        with open(config,'r') as f:
            self.event_q = IEFQ()
            data= json.load(f)
            self.xer_addr = data['xer']['addr']
            self.xer_port = data['xer']['port']
            self.xer_url = data['xer']['url']
            run_server(self.xer_addr, self.xer_port, self.event_q, self.xer_url)

        cache_ttl = data['icf']['cache_ttl']
        max_ttl = data['icf']['max_ttl']
        self.cache = Cache(cache_ttl, max_ttl)

    def _init(self):
        xer_listener = T.Thread(daemon=True, target=self._listen_xer)
        xer_listener.start()

    def _listen_xer(self):
        while True:
            event = self.event_q.get(block=True)
            self.cache.store_event_by_suci(event)
            #self.cache.store_event_by_guti(event)
            #self.cache.store_event_by_supi(event)


"""
import grpc

from pyli5.utils.logger import Logger
from pyli5.iface.li_xqr.xqr import LI_XQR
from pyli5.iface.li_xqr.xqr_server import XQRMessage, XQRPipe, X1Message
from pyli5.iface.x1.x1_messages import *
from pyli5.icf.server_pb2_grpc import *
from threading import Thread
import base64
class ICF():
    def __init__(self, xqr_addr : str, xqr_port : str, grcp_port : str):
        self.logger = Logger("ICF")
        self.xqr_pipe = XQRPipe()
        self.xqr = LI_XQR(self.logger)
        self.xqr.run_server(xqr_addr, int(xqr_port), "/", self.xqr_pipe)
        self.grpc_port = grcp_port
        self._arm()

    def _listen_xqr(self):
        while True:
            try:
                msg = self.xqr_pipe.get()
                if msg.msg.entity.type == "PrivateIdentityAssociationRequest":
                    #msg.responseQ.put((200,etree.tostring(
                    #    X1Message(
                    #        entity=PrivateIdentityAssociationRequest(
                    #            admf_id="ADMF_ID",
                    #            ne_id="ne-02",
                    #            x1_transaction_id=msg.msg.entity.x1_transaction_id,
                    #            pir_query=base64.b64encode("AAAAAAAAAAAAAAAAAA".encode())
                    #        )
                    #    ).xml_encode(), xml_declaration=True)))
                    answer = self.Query(msg.msg.entity.pir_query)
                    msg.responseQ.put((200, etree.tostring(
                    X1Message(
                        entity=PrivateIdentityAssociationResponse(
                            admf_id="ADMF_ID",
                            ne_id="ne-02",
                            x1_transaction_id=msg.msg.entity.x1_transaction_id,
                            pir_answer=answer)
                        )
                    .xml_encode(), xml_declaration=True)))
                #elif msg.msg.entity.type == "IdentityAssociationRequest":
                #    msg.responseQ.put((200,etree.tostring(
                #        X1Message(
                #            entity=IdentityAssociationResponse(
                #                admf_id="admfID",
                #                ne_id="neID",
                #                x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
                #                records=[IdentityAssociationRecord(
                #                    supi="123456789",
                #                    suci="AAAAAAAAAA",
                #                    fiveg_guti="5gguti-8475329759823",
                #                    start_time=get_time_utc(),
                #                    end_time=get_time_utc(),
                #                )]
                #            )
                #        ).xml_encode(), xml_declaration=True)))
            except Exception as ex:
                self.logger.error(str(ex))

    def Query(self, pir_query : str):
        """ Query local GRPC server for PIR """
        grpc_chan = grpc.insecure_channel(f'localhost:{self.grpc_port}')
        stub = InternalServerStub(grpc_chan)
        return stub.Query(pir_query)

    def _arm(self):
        t = Thread(daemon=True, target=self._listen_xqr)
        t.start()