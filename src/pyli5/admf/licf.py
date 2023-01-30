import json
import logging

from pyli5.iface.li_hiqr.li_hiqr import LI_HIQR
from pyli5.iface.li_hiqr.li_hiqr_server import HIQRPipe, H1_Q, HIQRMessage
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.utils.logger import Logger
from threading import Thread
from lxml import etree
from queue import Queue
class LICF:
    def __init__(self, h1_address : str, h1_port : str, li_admf : Queue()):
        self.logger = Logger("LICF")
        self.warrants = {} #doc_ref -> {"Header": header, "Warrant": document_object}
        self.li_admf = li_admf
        self.hiqr = LI_HIQR(self.logger)
        self.pipe = HIQRPipe()
        self.hiqr.run_server(h1_address, int(h1_port), self.pipe)
        self._arm()

    def _arm(self):
        t = Thread(daemon=True, target=self._dispatch_h1_messages, args=())
        t.start()

    def _dispatch_h1_messages(self):
        while True:
            msg = self.pipe.get()
            header = msg.msg.header
            payload = msg.msg.payload
            self.logger.log(f"LI_H1 - Received : {etree.tostring(msg.msg.xml_encode(), xml_declaration=True, pretty_print=True)}")
            response_header = Header(header.receiver, header.sender, header.transactionId)
            if payload.type == HI1_PAYLOAD_REQUEST:
                response_payload = Payload(HI1_PAYLOAD_RESPONSE, [], None)
                for action in payload.actions:
                    if action.type == HI1_ACTION_REQUEST and "CREATE" in action.verb and isinstance(action.object, Document_Object):
                        warrant = action.object
                        response_action = Action(HI1_ACTION_RESPONSE, "CREATEResponse", action.action_identifier, warrant.object_identifier, None)
                        self.warrants[warrant.doc_ref] = {"Header":header, "Warrant":warrant}
                    else:
                        response_action = Action(HI1_ACTION_RESPONSE, "ErrorInformation", action.action_identifier, None, None, ErrorInformation("Expected Document Object on H1 Interface", "500"))
                    response_payload.actions.append(response_action)
            else:
                self.logger.log("LI_HIQR - Expected Request", logging.ERROR)
                response_payload = Payload(HI1_PAYLOAD_RESPONSE, None, ErrorInformation("Expected Request", "500"))

            # send notification to LIPF
            self.logger.log(f"LI_ADMF - forwarding { {'Header':header, 'Warrant':warrant}}")
            self.li_admf.put({"Header":header, "Warrant":warrant})

            response = HI1_Message(response_header, response_payload)
            msg.responseQ.put((200, etree.tostring(response.xml_encode(), xml_declaration=True)))
