import threading
from pyli5.iface.x1.x1_messages import X1Message
from pyli5.iface.li_xqr.xqr_client import XQRClient
from pyli5.iface.li_xqr.xqr_server import XQRServer, XQRPipe, X1_Q
from pyli5.utils.logger import Logger

# Implements LI_XQR interface
class LI_XQR:
    """
    XQR interface between NE (ICF) <--> ADMF (IQF). Uses the X1 interface (TS 133 121) as per TS 133 128
    :param admf_id : id if this is ADMF, else None
    :param ne_id : id if this is NE, else if ADMF None
    """

    def __init__(self, logger : Logger):
        self.logger = logger
    def run_server(self, host: str, port: int, url: str, pipe: XQRPipe):
        """
        launches a HTTP server listening for POST request on LI_XEM1 interface
        It forwards requests to the X1 processing logic which will directly communicate with ADMF/NE
        :param host : ipv4 address
        :param port : port
        :param url : served url ("/X1/(ADMF or NE)/")
        :param taskQ : queue for receiving task messages from X1
        :param destinationQ: queue for receiving destination messages from X1
        :poram notifyQ : queue for sending notification on the result of one operation to X1 to generate responses
        """
        server = XQRServer(host, port, url, pipe, self.logger)
        t = threading.Thread(daemon=True, target=server.serve_forever, args=())
        t.start()
    def send(self, host: str, port: int, url: str, content: X1Message, source_address:tuple=None)->X1Message:
        """
        :param host: ipv4
        :param port: port
        :param url: "/X1/<NE or ADMF>"
        :param content: XML message compliant with TS 103 221
        :return:
        """


        client = XQRClient(self.logger, source_address)
        resp = client.send(host, port, url, content)
        return resp

