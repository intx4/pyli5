import json
import logging
import threading

from pyli5.iface.li_hiqr.li_hiqr import LI_HIQR
from pyli5.iface.li_hiqr.li_hiqr_server import HIQRPipe, H1_Q, HIQRMessage
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.utils.logger import Logger
from threading import Thread
from lxml import etree
from queue import Queue
from pyli5.iface.x1.x1 import *
from pyli5.iface.x1.x1_messages import *
from pyli5.iface.li_xqr.xqr import *
from pyli5.iface.li_xqr.xqr_client import *
from pyli5.iface.li_xqr.xqr_server import XQRMessage, XQRPipe
from pyli5.utils.logger import Logger
from threading import Thread
from lxml import etree
from queue import Queue
from pyli5.utils.identifiers import gen_random_uuid
from pyli5.admf.internal_iface import InternalInterface
from multiprocessing import Process
from threading import Lock, Thread
class AuthorizationStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.sender_id_to_auth_id = {}

    def put(self, k:str, v:str):
        self.lock.acquire()
        self.sender_id_to_auth_id[k] = v
        self.lock.release()

    def get(self, k:str)->str:
        self.lock.acquire()
        try:
            v = self.sender_id_to_auth_id[k]
        except:
            v = None
        finally:
            self.lock.release()
            return v

class LEAInfoStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.sender_id_to_auth_id = {}

    def put(self, k:str, v: tuple):
        self.lock.acquire()
        self.sender_id_to_auth_id[k] = v
        self.lock.release()

    def get(self, k:str)->tuple:
        self.lock.acquire()
        try:
            v = self.sender_id_to_auth_id[k]
        except:
            v = None
        finally:
            self.lock.release()
            return v

    def keys(self)->[str]:
        self.lock.acquire()
        keys = self.sender_id_to_auth_id.keys()
        self.lock.release()
        return keys
class IQF():
    def __init__(self, admf_id : str, hiqr_addr : str, hiqr_port : str, icf_addr : str, icf_port : str, li_iqf : InternalInterface):
        self.logger = Logger("IQF")
        self.xqr = LI_XQR(self.logger)
        self.admf_id = admf_id

        self.hiqr = LI_HIQR(self.logger)
        self.hiqr_pipe = HIQRPipe()
        self.hiqr.run_server(hiqr_addr, int(hiqr_port), self.hiqr_pipe)

        self.xqr = LI_XQR(self.logger)
        self.icf_addr = icf_addr
        self.icf_port = icf_port

        self.sender_auth = AuthorizationStore() #sender id -> auth ref
        self.x1_tid_to_sender = LEAInfoStore() #x1_tid -> (addr, port)

        self.li_iqf = li_iqf
        self._arm()

    def _dispatch_h1_messages(self):
        """

        """
        while True:
            try:
                msg = self.hiqr_pipe.get()
                self.logger.log("New message from LI_HIQR")
                header = msg.msg.header
                sender = header.sender.unique_identifier
                actions = msg.msg.payload.actions
                # currently cheks only if authorization is referenced
                response_actions = []
                response = None
                for i,action in enumerate(actions):
                    if action.type == HI1_ACTION_REQUEST:
                        if "CREATE" in action.verb:
                            if isinstance(action.object, Authorisation_Object):
                                self.sender_auth.put(sender,action.object.object_identifier)
                                response_actions.append(Action(HI1_ACTION_RESPONSE, "CREATEResponse", str(i), action.object.object_identifier, None))
                            if isinstance(action.object, LD_Task_Object):
                                found = False
                                for associated in action.object.associated:
                                    if associated in self.sender_auth.get(sender):
                                        found = True
                                        break
                                if not found:
                                    self.logger.error("Not Authorized : Referenced Auth Object not found")
                                    response_actions.append(Action(HI1_ACTION_RESPONSE, "ErrorInformation", str(i), None, None, error=ErrorInformation("Not Authorized : Referenced Auth Object not found", "1000")))
                                else:
                                    response_actions.append(
                                        Action(HI1_ACTION_RESPONSE, "CREATEResponse", str(i), action.object.object_identifier,
                                               None))
                                    t = threading.Thread(daemon=True, target=self._process_LD_task, args=(header, action, action.object.delivery_details.address, action.object.delivery_details.port))
                                    self.logger.log("Processing LD Task...")
                                    t.start()

                            if isinstance(action.object, Private_LD_Task_Object):
                                found = False
                                for associated in action.object.associated:
                                    if associated in self.sender_auth.get(sender):
                                        found = True
                                        break
                                if not found:
                                    self.logger.error("Not Authorized : Referenced Auth Object not found")
                                    response_actions.append(Action(HI1_ACTION_RESPONSE, "ErrorInformation", str(i), None, None,
                                                                   error=ErrorInformation(
                                                                       "Not Authorized : Referenced Auth Object not found",
                                                                       "1000")))

                                else:
                                    response_actions.append(
                                        Action(HI1_ACTION_RESPONSE, "CREATEResponse", str(i), action.object.object_identifier,
                                               None))
                                    t = threading.Thread(daemon=True, target=self._process_Private_LD_task, args=(
                                    header, action, action.object.delivery_details.address,
                                    action.object.delivery_details.port))
                                    self.logger.log("Processing Private LD Task...")
                                    t.start()

                response = Payload(HI1_PAYLOAD_RESPONSE, response_actions)

                msg.responseQ.put((
                    200,
                    etree.tostring(HI1_Message(
                    header=Header(sender=header.receiver, receiver=header.sender, transactionId=header.transactionId),
                    payload=response
                ).xml_encode(),xml_declaration=True,pretty_print=True)))

            except Exception as ex:
                self.logger.error(str(ex))
            finally:
                continue

    def _process_LD_task(self, header: Header, action: Action, addr : str, port : str):
        try:
            self.li_iqf.send_request(True)
            resp = self.li_iqf.get_response(True)
            if resp == False:
                self.logger.error("LI_IQF - LICF negates request: IEF not active")
                msg = HI1_Message(
                    header=Header(header.receiver, header.sender, header.transactionId),
                    payload=Payload(HI1_PAYLOAD_RESPONSE, [
                        Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None,
                               error=ErrorInformation("IEF not active", "1000"))
                    ])
                )
                self.hiqr.send(addr, int(port), "/", etree.tostring(msg.xml_encode(), xml_declaration=True))
                return
            self.logger.log("Forwarding LD Task to ICF")
            xqr_msg = self._convert_to_IdentityAssociation(action.object)
            self.logger.log("Waiting for response")
            response = self.xqr.send(self.icf_addr, self.icf_port,"/", xqr_msg)
            self.logger.log("Converting to HI1 Message")
            action_response = self._convert_from_IdentityAssociation(action.object.reference,
                                                                    action.object.object_identifier, response)
            response = Payload(HI1_PAYLOAD_REQUEST, actions=[action_response])
            msg = HI1_Message(
                header=Header(header.receiver, header.sender, header.transactionId),
                payload=response,
            )
            self.logger.log("Sending over to HIQR")
            self.hiqr.send(addr, int(port), "/",etree.tostring(msg.xml_encode(), xml_declaration=True))
        except Exception as ex:
            self.logger.error(str(ex))
            msg = HI1_Message(
                header=Header(header.receiver, header.sender, header.transactionId),
                payload=Payload(HI1_PAYLOAD_RESPONSE, [
                    Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None,
                           error=ErrorInformation(str(ex), "1000"))
                ])
            )
            self.hiqr.send(addr, int(port), "/", etree.tostring(msg.xml_encode(), xml_declaration=True), timeout=0.001)
            return

    def _process_Private_LD_task(self, header: Header, action: Action, addr : str, port : str):
        try:
            self.li_iqf.send_request(True)
            resp = self.li_iqf.get_response()
            if resp == False:
                self.logger.error("LI_IQF - LICF negates request: IEF not active")
                msg = HI1_Message(
                    header=Header(header.receiver, header.sender, header.transactionId),
                    payload=Payload(HI1_PAYLOAD_RESPONSE, [
                    Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None, error=ErrorInformation("IEF not active", "1000"))
                    ])
                )
                self.hiqr.send(addr, int(port), "/", etree.tostring(msg.xml_encode(), xml_declaration=True))
                return
            self.logger.log("Forwarding Private LD Task to ICF")
            xqr_msg = self._convert_to_PrivateIdentityAssociation(action.object)
            self.logger.log("Waiting for response")
            response = self.xqr.send(self.icf_addr, self.icf_port,"/", xqr_msg)
            self.logger.log("Converting to HI1 Message")
            action_response = self._convert_from_PrivateIdentityAssociation(action.object.reference,
                                                                    action.object.object_identifier, response)
            response = Payload(HI1_PAYLOAD_REQUEST, actions=[action_response])
            msg = HI1_Message(
                header=Header(header.receiver, header.sender, header.transactionId),
                payload=response,
            )
            self.logger.log("Sending over to HIQR")
            self.hiqr.send(addr, int(port), "/", etree.tostring(msg.xml_encode(), xml_declaration=True))
        except Exception as ex:
            self.logger.error(str(ex))
            msg = HI1_Message(
                header=Header(header.receiver, header.sender, header.transactionId),
                payload=Payload(HI1_PAYLOAD_RESPONSE, [
                    Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None,
                           error=ErrorInformation(str(ex), "1000"))
                ])
            )
            self.hiqr.send(addr, int(port), "/", etree.tostring(msg.xml_encode(), xml_declaration=True), timeout=0.001)
            return

    def _convert_to_IdentityAssociation(self, h1_msg : LD_Task_Object)->X1Message:
        x1_tid = gen_random_uuid()
        for x1_tid in self.x1_tid_to_sender.keys():
            x1_tid = gen_random_uuid()
        try:
            suci = h1_msg.details["SUCI"]
        except:
            suci = None
        try:
            tmsi = h1_msg.details["5GSTMSI"]
        except:
            tmsi = None
        try:
            guti = h1_msg.details["5GGUTI"]
        except:
            guti = None
        try:
            nr = h1_msg.details["NRCellIdentity"]
        except:
            nr = None
        try:
            tac = h1_msg.details["TrackingAreaCode"]
        except:
            tac = None

        return X1Message(IdentityAssociationRequest(self.admf_id, None, x1_transaction_id=x1_tid, observed_time=h1_msg.time, suci=suci, fiveg_guti=guti, fiveg_tmsi = tmsi, nr_cell_identity=nr, tracking_area_code=tac))

    def _convert_to_PrivateIdentityAssociation(self, h1_msg : Private_LD_Task_Object)->X1Message:
        x1_tid = gen_random_uuid()
        for x1_tid in self.x1_tid_to_sender.keys():
            x1_tid = gen_random_uuid()
        return X1Message(PrivateIdentityAssociationRequest(self.admf_id, None, x1_tid, h1_msg.query))

    def _convert_from_IdentityAssociation(self, reference : str, associated_object : str, x1_msg : X1Message)->Action:
        id = gen_random_uuid()
        return Action(HI1_ACTION_REQUEST, "DELIVER", "0", id, Delivery_Object(
            object_identifier=id,
            associated_objects=[associated_object],
            reference=reference,
            delivery_id=gen_random_uuid(),
            data=base64.b64encode(etree.tostring(x1_msg.xml_encode(), xml_declaration=True))
        ))

    def _convert_from_PrivateIdentityAssociation(self, reference : str, associated_object : str, x1_msg : X1Message)->Action:
        id = gen_random_uuid()
        return Action(HI1_ACTION_REQUEST, "DELIVER", "0", id, Delivery_Object(
            object_identifier=id,
            associated_objects=[associated_object],
            reference=reference,
            delivery_id=gen_random_uuid(),
            data=x1_msg.entity.pir_answer
        ))

    def _arm(self):
        t = threading.Thread(daemon=True, target=self._dispatch_h1_messages)
        t.start()