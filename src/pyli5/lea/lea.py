import base64
import threading
import time

from pyli5.iface.li_hiqr.li_hiqr import LI_HIQR
from pyli5.iface.li_hiqr.li_hiqr_server import HIQRPipe, H1_Q, HIQRMessage
from pyli5.iface.li_hiqr.li_hiqr_client import HIQRClient
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.iface.li_hiqr.hi1 import H1_Parser
from pyli5.utils.logger import Logger, MAXLEN
from pyli5.utils.math import Min
from pyli5.utils.identifiers import gen_random_uuid
from pyli5.lea.client_pb2 import QueryMessage, AnswerMessage
from pyli5.lea.client_pb2_grpc import ProxyServicer, add_ProxyServicer_to_server

from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import grpc

class TasksStatus():
    def __init__(self):
        self.lock = Lock()
        self.db = {}

    def put(self, id : str, answer : str, error=False):
        with self.lock:
            self.db[id] = (answer,error)

    def pop(self, id : str)->(str,bool):
        with self.lock:
            try:
                return self.db.pop(id)
            except KeyError:
                return None, False

    def get(self, id : str)->(str,bool):
        with self.lock:
            try:
                return self.db[id]
            except KeyError:
                return None
    def keys(self):
        with self.lock:
            return self.db.keys()



class LEA(ProxyServicer):
    def __init__(self, id : str, hiqr_addr : str, hiqr_port : str, iqf_addr : str, iqf_port : str, grpc_port : str):
        super().__init__()
        self.logger = Logger("LEA")
        self.id = id
        self.hiqr_addr = hiqr_addr
        self.hiqr_port = hiqr_port
        self.hiqr = LI_HIQR(self.logger)
        self.hiqr_pipe = HIQRPipe()
        self.hiqr.run_server(self.hiqr_addr, self.hiqr_port, self.hiqr_pipe)
        self.iqf_addr = iqf_addr
        self.iqf_port = iqf_port
        self.grpc_port = grpc_port
        self.task_status = TasksStatus()
        self._arm()

    def _listen_hiqr(self):
        """ Listen HIQR for DeliveryObjects and stores the response in task status to be fetched by gRPC logic """
        while True:
            try:
                msg = self.hiqr_pipe.get()
                self.logger.log(f"LI_HIQR IDENTITY ASSOCIATION RESPONSE: {etree.tostring(msg.msg.xml_encode(), pretty_print=True)[:Min(MAXLEN, len(etree.tostring(msg.msg.xml_encode())))]}")
                if msg.msg.payload.actions[0].error is None and msg.msg.payload.actions[0].object is not None:
                    msg.responseQ.put((
                        200,
                        etree.tostring(HI1_Message(
                            header=Header(msg.msg.header.receiver, msg.msg.header.sender, msg.msg.header.transactionId),
                            payload=Payload(HI1_PAYLOAD_RESPONSE, [Action(HI1_ACTION_RESPONSE, "DELIVERResponse", "0",
                                                                          msg.msg.payload.actions[0].identifier, None)])
                        ).xml_encode(), xml_declaration=True)
                    ))
                    self.task_status.put(msg.msg.header.transactionId, msg.msg.payload.actions[0].object.data.decode())
                else:
                    self.task_status.put(msg.msg.header.transactionId, msg.msg.payload.actions[0].error.code+": "+msg.msg.payload.actions[0].error.desc, error=True)
            except Exception as ex:
                self.logger.error(f"LI_HIQR {str(ex)}")

    def send(self, msg : HI1_Message):
        resp = self.hiqr.send(self.iqf_addr, self.iqf_port, "", etree.tostring(msg.xml_encode(), xml_declaration=True))
        if resp is not None:
            if resp.payload.error is not None:
                self.logger.error(f"HIQR ErrorInformation: {resp.payload.error.code} {resp.payload.error.desc}")
            for action in resp.payload.actions:
                if action.error is not None:
                    self.logger.error(f" HIQR ErrorInformation: {action.error.code} {action.error.desc}")

    def Query(self, request, context):
        """ Receives gRPC request from PIR logic, forwards to IQF, returns HIQR response as gRPC response"""
        self.logger.log(f"gRCP - Received request {request.query[:Min(MAXLEN, len(request.query))]}")
        try:
            tx_id = gen_random_uuid()
            while tx_id in self.task_status.keys():
                tx_id = gen_random_uuid()
            header = Header(HeaderIdentifier("XX", self.id), HeaderIdentifier("XX", "ACTOR02"),
                            transactionId=tx_id)

            auth_id = gen_random_uuid()
            task_id = gen_random_uuid()
            while task_id == auth_id:
                task_id = gen_random_uuid()

            payload = Payload(HI1_PAYLOAD_REQUEST, [
                Action(HI1_ACTION_REQUEST, "CREATE", "0", None, Authorisation_Object(
                    object_identifier=auth_id,
                    auth_reference="W000001",
                    start_time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    end_time=(datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                )),
                Action(HI1_ACTION_REQUEST, "CREATE", "1", None, Private_LD_Task_Object(
                    object_identifier=task_id,
                    associated_objects=[auth_id],
                    reference=f"LD-0-{len(self.task_status.keys())}",
                    query=request.query,
                    delivery_details=Delivery_Details(address=self.hiqr_addr, port=self.hiqr_port)
                ))
            ])

            self.task_status.put(tx_id, "")

            msg = HI1_Message(header, payload)
            self.send(msg)

            time.sleep(0.01)
            while self.task_status.get(tx_id)[0] == "":
                time.sleep(0.1)
            if self.task_status.get(tx_id)[0] != "":
                data, error = self.task_status.pop(tx_id)
                if not error:
                    return AnswerMessage(answer=data, error="")
                else:
                    return AnswerMessage(answer="", error=data)
        except Exception as ex:
            self.logger.log(f"gRPC - error {str(ex)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(ex))

    def _arm(self):
        hiqr_listener = threading.Thread(daemon=True, target=self._listen_hiqr)
        hiqr_listener.start()

        grpc_listener = threading.Thread(daemon=True, target=self._listen_grpc)
        grpc_listener.start()

    def _listen_grpc(self):
        try:
            grpc_service = grpc.server(ThreadPoolExecutor(),
                                       options=[('grpc.max_send_message_length', 200 *1024*1024),
                                                ('grpc.max_receive_message_length', 200 *1024*1024)])#200 MB
            add_ProxyServicer_to_server(self, grpc_service)
            grpc_service.add_insecure_port(f"127.0.0.1:{self.grpc_port}")
            grpc_service.start()
            self.logger.log(f"gRPC - started service at 127.0.0.1:{self.grpc_port}")
            grpc_service.wait_for_termination()
        except Exception as ex:
            self.logger.log(f"gRPC - Error starting server {str(ex)}")
