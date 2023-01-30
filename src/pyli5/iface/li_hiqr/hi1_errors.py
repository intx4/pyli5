from pyli5.iface.li_hiqr.hi1_messages import Header

class NotImplementedError(Exception):
    def __init__(self, info: str):
        self.message = "Not implemented: " + info
        self.header = None
        super().__init__(self.message)

class XMLError(Exception):
    def __init__(self, info: str):
        self.header = None
        self.message = "XML Parsing error: " + info
        super().__init__(self.message)

class FormatError(Exception):
    def __init__(self, info: str):
        self.header = None
        self.message = "XML Object format does not respect specification: " + info
        super().__init__(self.message)
class GenericError(Exception):
    def __init__(self, info: str):
        self.header = None
        self.message = "Error info: " + info
        super().__init__(self.message)

class ChecksumError(Exception):
    def __init__(self, info: str):
        self.header = None
        self.message = "Checksum mismatch:" + info
        super().__init__(self.message)