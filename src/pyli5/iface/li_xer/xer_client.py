import base64
import logging
from threading import Thread
from http import client
from pyli5.utils.logger import Logger
from pyli5.ief.ief_records import IEFRecord, IEFAssociationRecord, IEFDeassociationRecord
from pyli5.iface.li_xer.pyasn import encode

class XERClient():

    def __init__(self, logger : Logger):
        self.logger = logger

    def _ber_encode(self, event: IEFRecord) -> bytes:
        return encode(event)

    def send(self, host: str, port : int, msg: IEFRecord):
        try:
            content = self._ber_encode(msg)
            content = base64.b64encode(content)
            connection = client.HTTPConnection(host, port=port)
            headers = {'Content-type': 'text/html', 'Content-Length': len(content)}
            connection.request("POST", "/", content, headers)
            self.logger.log(f"  LI_XER_Client - sending {content} to {host}:{port}")
            response = connection.getresponse()
            self.logger.log(f"  LI_XER_Client - sending {response.read().decode()} to {host}:{port}")
        except Exception as ex:
            self.logger.error(str(ex))