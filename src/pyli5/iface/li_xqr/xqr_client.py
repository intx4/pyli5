from http import client
from pyli5.iface.x1.x1 import X1Parser
from pyli5.iface.x1.x1_messages import X1Message
from pyli5.utils.logger import Logger
from threading import Thread
from lxml import etree

class XQRClient():
    """
    Implements an HTTP client sending POST request according to X1 model TS 103 221, on LI_XEM1 interface
    It forwards responses from servers to the X1 processing logic which will directly communicate with ADMF/NE
    for status notification.
    :param notifyQ : queue used for receiving responses to previous requests from X1
    :param admf_id : ID of this ADMF, None if this is not ADMF
    :param ne_id : ID of this NE, None if this is not a NE
    """
    def __init__(self, logger : Logger, source_address:tuple=None):
        self.logger = logger
        self.x1_parser = X1Parser()
        self.source_address = source_address

    # send a compliant X1 message. Spawns a thread
    def send(self, host: str, port : int, url: str, content: X1Message) -> X1Message:
        try:
            connection = client.HTTPConnection(host, port=port, source_address=self.source_address)
            content = etree.tostring(content.xml_encode(), xml_declaration=True)
            headers = {'Content-type': 'application/xml', 'Content-Length': len(content)}

            connection.request("POST", url, content, headers)

            response = connection.getresponse()
            self.logger.log(f"  XQR_Client - sending {content} to {host}:{port} at {url}")
            msg = self.x1_parser.parse_X1_Message(response.read())
            self.logger.log(f"  XQR_Client - receiving {etree.tostring(msg.xml_encode(), pretty_print=True)} from {host}:{port} ")
            connection.close()
            return msg
        except Exception as ex:
            self.logger.error(f"    XQR CLIENT - {str(ex)}")


