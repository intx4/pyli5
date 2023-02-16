from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pyli5.iface.x1.x1 import X1Parser
from pyli5.utils.logger import Logger, MAXLEN
from pyli5.utils.math import Min
from pyli5.iface.x1.x1_messages import *
from pyli5.iface.x1.x1_errors import *
from queue import Queue
from dataclasses import dataclass

class X1_Q(Queue):
    """ Queue for X1Message"""
    def __init__(self, maxsize=0):
        self.q = Queue(maxsize)

    def get(self, block=True) -> X1Message:
        return self.q.get(block)

    def put(self, msg: X1Message, block=True):
        self.q.put(msg, block)

    def empty(self) -> bool:
        return self.q.empty()

@dataclass
class XQRMessage:
    msg : X1Message #message passed from iface to logic
    responseQ: Queue #channel to receive (code:int, resp:etree.tostring(X1message.xml_encode())) from logic

class XQRPipe:
    def __init__(self, ):
        self.upL = X1_Q()

    def push(self, msg: XQRMessage):
        """ Iface to logic"""
        self.upL.put(msg)

    def get(self)->XQRMessage:
        """ Logic reads from iface"""
        return self.upL.get()



class XQRServer(ThreadingHTTPServer):
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
    def __init__(self, addr: str, port: int, serving_path: str, xqr_pipe: XQRPipe, logger : Logger):
        self.addr = addr
        self.port = port
        self.serving_path = serving_path
        self.x1_parser = X1Parser()
        self.xqr_pipe = xqr_pipe
        self.logger = logger
        super().__init__((addr, port), RequestHandlerClass=XQRHandler)
        self.logger.log(f"  XQR_Server - started at {addr}:{port}")

class XQRHandler(BaseHTTPRequestHandler):
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
        if self.path != self.server.serving_path:
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.server.logger.log("XQR_Server - Received POST request")
        try:
            msg = self.server.x1_parser.parse_X1_Message(post_data)
            self.server.logger.log(f"   XQR_Server - {etree.tostring(msg.xml_encode())[:Min(MAXLEN, len(etree.tostring(msg.xml_encode())))]}")
            q=Queue(1)
            self.server.xqr_pipe.push(XQRMessage(msg=msg, responseQ=q))
            resp_code, resp_content = q.get()
            if resp_code == 500:
                raise Exception("Internal Server Error")
        except X1MessageError as ex:
            if "TopLevel" in ex.type_for_error:
                err_msg = X1Message(entity=None, error=TopLevelErrorResponse(ex.admf_id, ex.ne_id))
            else:
                err_msg = X1Message(
                    entity=SimpleResponse(ex.admf_id, ex.ne_id, ex.x1_tid, None, error=str(ex), code=ex.code,
                                          type_for_error=ex.type_for_error, type="ErrorResponse"))
                resp_code, resp_content = 500, etree.tostring(err_msg.xml_encode())
        except Exception as ex:
            self.server.logger.error(f"XQR_Server error - {str(ex)}")
            resp_code, resp_content = 500, b"Internal server error"
        finally:
            self.server.logger.log(f"   XQR_Server - sending response {resp_code} : {resp_content.decode()[:Min(MAXLEN, len(resp_content.decode()))]}")
            if resp_code != 0:
                self._set_response(resp_code, resp_content)

