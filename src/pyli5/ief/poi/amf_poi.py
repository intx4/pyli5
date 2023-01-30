import logging
import queue
import string
import time
import json
import re
from datetime import datetime
from queue import Queue
from os import path
from threading import Thread
from pyli5.ief.ief_records import IEFRecord, IEFQ, IEFAssociationRecord, IEFDeassociationRecord
from pyli5.utils.logger import Logger
from pyli5.utils.time import get_time_utc
import string

#explore("http2")
#pcap = rdpcap('ue_auth_amf_to_ausf.pcapng')

TTL = 600.0


#class AMFSniffer(Watcher):
#    """
#    This watcher sniffs the traffic between AMF and AUSF to capture suci to supi association. Deprecated in favor of AMFLogWatcher
#    """
#    def __init__(self, ausf_ip : str, ausf_port : int, ausf_re : str, iface : str, q : Queue, shut_down : Queue):
#        super().__init__(q=q, shut_down=shut_down)
#        self.ausf_ip = ausf_ip
#        self.ausf_port = ausf_port
#        self.ausf_re = ausf_re
#        self.iface = iface
#        """
#        maps for interception workflow:
#        1 - AMF request is sent as http2 stram with suci -> save stream id - suci into A
#        2 - AUSF sends response with the same stream id as in 1 with an url for delivery the auth challenge response -> retrieve suci from A with stream id and save url - suci to B
#        3 - AMF forwards challenge response as http2 request to the url in B with a new stream id -> save new stream id - suci (provided from B) to C
#        4 - AUSF replies with supi using the stream id from C -> save suci (from C) - supi association and viceversa
#        """
#        self.stream_to_suci_A = ExpiringDict(max_age_seconds=TTL)
#        self.delivery_to_suci_B = ExpiringDict(max_age_seconds=TTL)
#        self.stream_to_suci_C = ExpiringDict(max_age_seconds=TTL)
#
#    def _get_supi(self, pkt : Packet):
#        pkt.decode_payload_as(h2.H2Frame)
#        p = pkt.payload
#        stream_id = p.stream_id
#        if p.type is None:
#            return
#        elif p.type == 1:
#            for hdr in p.hdrs:
#                if type(hdr) == h2.HPackLitHdrFldWithoutIndexing:
#                    dest = hdr.hdr_value.data
#                    dest = dest[(dest.index('(') + 1):-1]  # strip garbage
#                    m = re.search(self.ausf_re, dest)
#                    if m is not None:
#                        if m.group() in self.delivery_to_suci_B:
#                            self.stream_to_suci_C[stream_id] = self.delivery_to_suci_B[m.group()]
#        elif p.type == 0:
#            # data
#            data = json.loads(p.data)
#            try:
#                suci = data['supiOrSuci']
#                self.stream_to_suci_A[stream_id] = suci
#            except KeyError:
#                try:
#                    m = re.search(self.ausf_re, data['_links']['5g-aka']['href'])
#                    if m is not None:
#                        url = m.group()
#                        if stream_id in self.stream_to_suci_A.keys():
#                            self.delivery_to_suci_B[url] = self.stream_to_suci_A[stream_id]
#                except KeyError:
#                    try:
#                        if data['authResult'] == "AUTHENTICATION_SUCCESS" and (
#                                stream_id) in self.stream_to_suci_C.keys():
#                            self.q.put([self.stream_to_suci_C[stream_id], data['supi']])
#                    except KeyError:
#                        return
#    def _stop(self):
#        while True:
#            try:
#                kill = self.shut_down.get(True, 1.0)
#                return
#            except queue.Empty:
#                continue
#    def watch(self):
#        sniff(filter=f"tcp and ( (src host {self.ausf_ip} and src port {self.ausf_port} ) or (dst host {self.ausf_ip} and dst port {self.ausf_port} )", iface=self.iface, prn=self._get_supi, stop_filter=self._stop)


class AMFLogWatcher():
    """
    Observers open5gs amf.log file to find IEF logging entries
    This is compatible with https://github.com/intx4/open5gs branch v2.4.10 modified open5gs-amfd binary with log level INFO

    :param path : str - path to log file
    :q : IEFQ - for sending ief assoc/deassoc events to poi logic
    :shut_down : - queue[bool] for triggering shutdown of interception
    """
    IEF_ASSOC_RE = r"IEF --- ASSOCIATION --- SUPI=\[([a-zA-F0-9-]{16,100})\], 5G-S_GUTI=\{AMF_ID:\[(0x[0-9A-Fa-f]{5})\],M_TMSI:\[(0x[0-9A-Fa-f]{8})\]\}, SUCI=\[([a-zA-F0-9-]{16,100})\], nCGI=\{pLMNID:\[([0-9a-fA-F]{6})\], nCI:\[0x([0-9a-fA-F]{2})\]\}, nCGITime=\[([0-9a-zA-Z:\-.]{20,30})\], tAI=\{pLMNID:\[([0-9a-fA-F]{6})\],tAC:\[([0-9]{1,4})\]\}, pEI=\[([a-zA-Z0-9-]{0,40})\], fiveGSTAIList=\[([0-9]?[\s0-9,]*[\s0-9]?)\]"
    IEF_DEASSOC_RE = r"IEF --- DEASSOCIATION --- SUPI=\[([a-zA-F0-9-]{16,100})\], 5G-S_GUTI=\{AMF_ID:\[(0x[0-9A-Fa-f]{5})\],M_TMSI:\[(0x[0-9A-Fa-f]{8})\]\}, SUCI=\[([a-zA-F0-9-]{16,100})\], nCGI=\{pLMNID:\[([0-9a-fA-F]{6})\], nCI:\[0x([0-9a-fA-F]{2})\]\}, nCGITime=\[([0-9a-zA-Z:\-.]{20,30})\], tAI=\{pLMNID:\[([0-9a-fA-F]{6})\],tAC:\[([0-9]{1,4})\]\}"
    def __init__(self, path : str, q : IEFQ, logger : Logger):
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
                    m = re.search(AMFLogWatcher.IEF_ASSOC_RE, line)
                    if m is not None:
                        event = IEFRecord()
                        supi, amf_id, tmsi, suci, plmn_id, nci, ncgi_time, _, tac, pei, list_of_tai = m.groups()
                        supi = supi.lstrip("imsi-")
                        pei = pei.lstrip("imeisv-")
                        plmn_id = "".join([c for c in plmn_id if c in string.digits])
                        list_of_tai = list_of_tai.split(", ")
                        list_of_tai = [plmn_id + t[0] for t in list_of_tai]
                        guti = amf_id + tmsi[2:]
                        guti = hex(int(bin(int(guti, 16))[2 + 8:], 2))[2:]  # skip first octet as per TS 124.500
                        tai = plmn_id + tac
                        event.assoc = IEFAssociationRecord(supi=supi, fivegguti=guti, suci=suci,
                                                           ncgi={'nCI': nci, 'pLMNID': plmn_id[-3:]}, ncgi_time=ncgi_time,
                                                           tai=tai,
                                                           timestmp=get_time_utc(), pei=pei, list_of_tai=list_of_tai)

                        self.logger.log(f"      AMF POI - new association event {event.assoc.supi} -> {event.assoc.suci} -> {event.assoc.fivegguti}")
                        self.q.put(event, block=True)
                    else:
                        m = re.search(AMFLogWatcher.IEF_DEASSOC_RE, line)
                        if m is not None:
                            event = IEFRecord()
                            supi, amf_id, tmsi, suci, plmn_id, nci, ncgi_time, _, tac = m.groups()
                            supi = supi.lstrip("imsi-")
                            guti = amf_id + tmsi[2:]
                            guti = hex(int(bin(int(guti,16))[2+8:],2))[2:] #skip first octet as per TS 124.500
                            plmn_id = "".join([c for c in plmn_id if c in string.digits])
                            event.deassoc = IEFDeassociationRecord(supi=supi,
                                                                   suci=suci,
                                                                   fivegguti=guti,
                                                                   ncgi={'nCI':nci, 'pLMNID':plmn_id[-3:]},
                                                                   ncgi_time=ncgi_time, timestmp=get_time_utc())
                            self.logger.log(
                                f"      AMF POI - new deassoc event {event.deassoc.supi} -> {event.deassoc.fivegguti}")
                            self.q.put(event, block=True)
                else:
                    time.sleep(0.1)
                    continue
        except Exception as ex:
            self.logger.error(f"        AMF POI - panic {str(ex)}")
            log.close()

class AMFPoi():
    """
    AMF POI. Provides supi <-> suci and supi <-> 5G-guti associations by sniffing AMF <-> AUSF traffic and observing AMF logs. Implements Poi
    :param config: json config file
    :param iefQ queue for passing interception products to the ief logic to be sent to ICF
    :param shut_down : queue for receiving shutdown signal from ief to stop interception
    """
    def __init__(self, path: str, ief_q : IEFQ,  logger):
        self.active = False

        log_path = path
        self.amf_logger = AMFLogWatcher(log_path, ief_q, logger)

        self.logger = logger

    def intercept(self):
        if self.active:
            return
        self.logger.log("   AMF POI - activated!")
        self.active = True
        #self.sniffer.watch()
        watcher = Thread(daemon=True, target=self.amf_logger.watch)
        watcher.start()


if __name__ == "__main__":
    iefq = IEFQ()
    poi = AMFPoi("./config/amf.json", iefq, logger=Logger("AMF POI"))
    poi.intercept()
    while True:
        print(iefq.get())
