import time
from http import client
from pyli5.iface.li_hiqr.hi1 import H1_Parser, HI1_Message
from pyli5.utils.logger import Logger, MAXLEN
from pyli5.utils.math import Min
from threading import Thread
from lxml import etree

class HIQRClient():
    """

    """
    def __init__(self, logger : Logger, source_address:tuple=None):
        self.logger = logger
        self.h1_parser = H1_Parser()
        self.source_addr = source_address

    # send a compliant X1 message.
    def send(self, host: str, port: int, url: str, content: str, timeout:float=None)->HI1_Message:
        self.logger.log(f"LI_HIQR_Client - sending {content[:Min(MAXLEN, len(content))]} to {host}:{port} at {url}")
        try:
            connection = client.HTTPConnection(host, port=port, source_address=self.source_addr, timeout=timeout)
            headers = {'Content-type': 'application/xml', 'Content-Length': len(content)}

            connection.request("POST", url, content, headers)
            response = connection.getresponse()
            resp = self.h1_parser.parse_HI1Message(response.read())
            self.logger.log(f"LI_HIQR_Client - receiving from {etree.tostring(resp.xml_encode(), pretty_print=True)[:Min(MAXLEN, len(etree.tostring(resp.xml_encode(), pretty_print=True)))]} {host}:{port} at {url}")
            connection.close()
            return resp
        except Exception as ex:
            self.logger.error(f"LI_HIQR_Client - {str(ex)}")
            raise ex