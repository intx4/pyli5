from dataclasses import dataclass
from queue import Queue
@dataclass
class IEFAssociationRecord():
    supi: str
    fivegguti: str
    timestmp: str  # utc
    tai: str
    ncgi: {}  # nCI -> v, pLMNID -> v
    ncgi_time: str  # last ueLocationTimestmp or nCGIs available
    suci: str
    pei: str
    list_of_tai: [str]


@dataclass
class IEFDeassociationRecord():
    supi: str
    fivegguti: str
    timestmp: str
    ncgi: {}  # nCI -> v, pLMNID ->
    ncgi_time: str
    suci: str #added for consistency with our PIR storage ICF


@dataclass
class IEFRecord():
    assoc: IEFAssociationRecord = None
    deassoc: IEFDeassociationRecord = None

class IEFQ(Queue):
    def __init__(self, maxsize=0):
        self.q = Queue(maxsize)

    def get(self, block=True) -> IEFRecord:
        return self.q.get(block)

    def put(self, n: IEFRecord, block=True):
        self.q.put(n, block)

    def empty(self) -> bool:
        return self.q.empty()

