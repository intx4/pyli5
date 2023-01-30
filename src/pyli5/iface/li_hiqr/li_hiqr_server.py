from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pyli5.iface.li_hiqr.hi1 import H1_Parser
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.utils.logger import Logger
from queue import Queue
from dataclasses import dataclass
from pyli5.iface.li_hiqr.hi1_errors import *

class H1_Q(Queue):
    """ Queue for HI1Message"""
    def __init__(self, maxsize=0):
        self.q = Queue(maxsize)

    def get(self, block=True) -> HI1_Message:
        return self.q.get(block)

    def put(self, msg: HI1_Message, block=True):
        self.q.put(msg, block)

    def empty(self) -> bool:
        return self.q.empty()

@dataclass
class HIQRMessage:
    msg : HI1_Message #message passed from iface to logic
    responseQ: Queue #channel to receive (code:int, resp:etree.tostring(HI1Message.xml_encode())) from logic

class HIQRPipe:
    """ Wrapper for communication between iface and logic """
    def __init__(self):
        self.upL = H1_Q()

    def push(self, msg: HIQRMessage):
        """ Iface to logic"""
        self.upL.put(msg)

    def get(self)->HIQRMessage:
        """ Logic reads from iface"""
        return self.upL.get()



class HIQRServer(ThreadingHTTPServer):
    """
    Implements an HTTP server listening for POST request on LI_XEM1 interface
    It forwards requests to the X1 processing logic which will directly communicate with ADMF/NE
    :param addr : ipv4 address
    :param port : port
    :param serving_path : served url ("/X1/(ADMF or NE)/")
    :param taskQ : queue for receiving task messages from X1
    :param destinationQ: queue for receiving destination messages from X1
    :poram notifyQ : queue for sending notification on the result of one operation to X1 to generate responses
    :param admf_id : ID of this ADMF, None if this is not ADMF
    :param ne_id : ID of this NE, None if this is not a NE
    """
    def __init__(self, addr: str, port: int, hiqr_pipe: HIQRPipe, logger: Logger):
        self.addr = addr
        self.port = port
        self.h1_parser = H1_Parser()
        self.hiqr_pipe = hiqr_pipe
        self.logger = logger
        super().__init__((addr, int(port)), RequestHandlerClass=H1_Handler)
        self.logger.log(f"  LI_HIQR_Server - started at {addr}:{port}")

class H1_Handler(BaseHTTPRequestHandler):
    def _set_response(self, code : int, content : bytes):
        self.send_response(code)
        if code == 200:
            type = "application/xml"
        else:
            type = "text/html"
        self.send_header('Content-type', type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        self.send_error(405, "Method not implemented")

    def do_HEAD(self):
        self.send_error(405, "Method not implemented")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.server.logger.log(f"   LI_HIQR Server - Received POST request {post_data.decode()}")
        try:
            msg = self.server.h1_parser.parse_HI1Message(post_data)
            self.server.logger.log(f"   LI_HIQR Server - H1 recvd message: {etree.tostring(msg.xml_encode())}")
            q=Queue(1)
            hiqr_msg = HIQRMessage(msg=msg, responseQ=q)
            self.server.hiqr_pipe.push(hiqr_msg)
            resp_code, resp_content = q.get()
        except XMLError as ex:
            # top level error
            self.server.logger.error(str(ex))
            err_msg = HI1_Message(header=ex.header,
                                  payload=Payload(HI1_PAYLOAD_RESPONSE, None, error=ErrorInformation(str(ex), "500")))
            resp_code, resp_content = 500, etree.tostring(err_msg.xml_encode())
        except Exception as ex:
            #nested error
            self.server.logger.error(f"   LI_HIQR Server - {str(ex)}")
            err_msg = HI1_Message(header=ex.header,payload = Payload(HI1_PAYLOAD_RESPONSE, [
        Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None, error=ErrorInformation(str(ex),"500"))
    ]))
            resp_code, resp_content = 500, etree.tostring(err_msg.xml_encode())
        finally:
            self.server.logger.log(f"   LI_HIQR Server - sending response to POST {resp_code} : {resp_content.decode()}")
            if resp_code != 0:
                self._set_response(resp_code, resp_content)