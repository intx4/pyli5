import threading
from pyli5.iface.li_hiqr.li_hiqr_server import HIQRServer
from pyli5.iface.li_hiqr.li_hiqr_client import HIQRClient
from threading import Lock
from pyli5.utils.logger import Logger
from pyli5.iface.li_hiqr.hi1_messages import HI1_Message
# Implements LI_XEM1 interface
class LI_HIQR:

    def __init__(self, logger: Logger):
        self.logger = logger
    def run_server(self, host: str, port: int, hiqr_pipe):
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
        server = HIQRServer(host, port, hiqr_pipe, self.logger)
        t = threading.Thread(daemon=True, target=server.serve_forever, args=())
        t.start()

    def send(self, host: str, port: int, url: str, content: str, source_address:tuple=None, timeout:float=None)->HI1_Message:
        """
        :param host: ipv4
        :param port: port
        :param url: "/X1/<NE or ADMF>"
        :param content: XML message compliant with TS 103 221
        :return:
        """

        client = HIQRClient(self.logger, source_address=source_address)
        resp = client.send(host, port, url, content, timeout=timeout)
        return resp