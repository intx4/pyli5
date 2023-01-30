import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pyli5.utils.logger import Logger
import logging
from pyli5.iface.li_xer import asn
from pyli5.ief.ief import IEFRecord, IEFDeassociationRecord, IEFAssociationRecord, IEFQ
from pyli5.iface.li_xer.pyasn import decode

class XERServer(ThreadingHTTPServer):
    """
    Implements an HTTP server listening for POST request on LI_XER interface
    :param addr : ipv4 address
    :param port : port
    :param serving_path : served url ("/X1/(ADMF or NE)/")
    :param q : Queue for passing events from IEF to ICF
    """
    def __init__(self, addr: str, port: int, q : IEFQ):
        self.addr = addr
        self.port = port
        self.logger = Logger("XER_SERVER", "")
        self.q = q
        super().__init__((addr, port), RequestHandlerClass=XERHandler)

class XERHandler(BaseHTTPRequestHandler):

    def _set_response(self, code : int):
        self.send_response(code)

    def do_GET(self):
        self.send_error(405, "Method not implemented")

    def do_HEAD(self):
        self.send_error(405, "Method not implemented")

    def _ber_decode(self, ber_ecd: bytes) -> IEFRecord:
        try:
            event = decode(ber_ecd)
            return event
        except Exception as ex:
            self.logger.log(ex, logging.ERROR)

    def do_POST(self):
        if self.path != self.server.serving_path:
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            self.server.logger.log(f"Received POST request {post_data.decode()}")
            self.server.q.put(self._ber_decode(bytearray(post_data)))
            self._set_response(200)
        except Exception as ex:
            self.server.logger.log(str(ex), logging.ERROR)
            self._set_response(500)


def run_server(addr: str, port: int, q : IEFQ):
    """
    Spawns an http server listening for events from IEF(s) on a separate thread
    :param addr: ipv4
    :param port: tcp port
    :param serving_path: url for request
    :param q: queue for passing to the ICF new IEF events
    :return:
    """
    server = XERServer(addr, port, q)
    t = threading.Thread(daemon=True, target=server.serve_forever, args=())
    t.start()
