import base64

from lxml import etree
from pyli5.iface.x1.x1_xml import *
import datetime
from pyli5.utils.time import get_time_utc
NSMAP={
    "ns1":"http://uri.etsi.org/03221/X1/2017/10",
    "ns2":"http://uri.etsi.org/03280/common/2017/07",
    "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "identity": "urn:3GPP:ns:li:3GPPIdentityExtensions:r17:v3",
}
ns1_ns = "{"+NSMAP['ns1']+"}"
ns2_ns = "{"+NSMAP['ns2']+"}"
xsi_ns = "{"+NSMAP['xsi']+"}"
identity_ns = "{"+NSMAP['identity']+"}"
class X1Entity():
    def __init__(self, admf_id, ne_id, x1_transaction_id,type):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.type = type
    def xml_encode(self)->etree.Element:
        pass


class ActivateTaskRequest(X1Entity):
    def __init__(self,  admf_id, ne_id, x1_transaction_id, xId, dIds):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.xId = xId
        self.dIds = dIds
        self.type = TYPE_ACTIVATETASK+"Request"

    def xml_encode(self):
        req = etree.Element(ns1_ns+"x1RequestMessage")
        req.attrib[xsi_ns+"type"] = "ns1:"+self.type

        admf_id = etree.SubElement(req, ns1_ns+ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns+NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns+TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns+X1TID)
        x1_tid.text = self.x1_transaction_id

        task_details = etree.SubElement(req, ns1_ns+"taskDetails")
        xId = etree.SubElement(task_details, ns1_ns+TASK_XID)
        xId.text = self.xId

        target_identifiers = etree.SubElement(task_details, ns1_ns+"targetIdentifiers")
        target_identifier = etree.SubElement(target_identifiers, ns1_ns+"targetIdentifier")
        extension = etree.SubElement(target_identifier, ns1_ns+"targetIdentifierExtension")
        owner = etree.SubElement(extension, ns1_ns+"Owner")
        owner.text = "3GPP"
        identity_ass = etree.SubElement(extension, identity_ns+"IdentityAssociationTargetIdentifier")

        delivery = etree.SubElement(task_details, ns1_ns+"deliveryType")
        delivery.text = "X2Only"

        list_dIds = etree.SubElement(task_details, ns1_ns+"listOfDIDs")
        for dId in self.dIds:
            d = etree.SubElement(list_dIds, ns1_ns+"dId")
            d.text = dId

        return req

class DeactivateTaskRequest(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, xId):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.xId = xId
        self.type = TYPE_DEACTIVATETASK + "Request"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1RequestMessage")
        req.attrib[xsi_ns + "type"] = "ns1:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id


        xId = etree.SubElement(req, ns1_ns + TASK_XID)
        xId.text = self.xId

        return req
class CreateDestinationRequest(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, dId, address, port):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.dId = dId
        self.address = address
        self.port = port
        self.type = TYPE_CREATEDESTINATION + "Request"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1RequestMessage")
        req.attrib[xsi_ns + "type"] = "ns1:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        dest_details = etree.SubElement(req, ns1_ns + "destinationDetails")
        dId = etree.SubElement(dest_details, ns1_ns + DESTINATION_DID)
        dId.text = self.dId



        delivery = etree.SubElement(dest_details, ns1_ns + "deliveryType")
        delivery.text = "X2Only"

        del_addr = etree.SubElement(dest_details, ns1_ns + "deliveryAddress")
        ip_address_and_port = etree.SubElement(del_addr, ns1_ns + "ipAddressAndPort")
        address = etree.SubElement(ip_address_and_port, ns2_ns + "address")
        ipv4 = etree.SubElement(address, ns2_ns + "IPv4Address")
        ipv4.text = self.address
        port = etree.SubElement(ip_address_and_port, ns2_ns + "port")
        tcp = etree.SubElement(port, ns2_ns + "TCPPort")
        tcp.text = self.port

        return req

class RemoveDestinationRequest(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, dId):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.dId = dId
        self.type = TYPE_REMOVEDESTINATION + "Request"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1RequestMessage")
        req.attrib[xsi_ns + "type"] = "ns1:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id


        dId = etree.SubElement(req, ns1_ns + DESTINATION_DID)
        dId.text = self.dId

        return req

class TopLevelErrorResponse():
    def __init__(self, admf_id, ne_id):
        self.admf_id = admf_id
        self.ne_id = ne_id

    def xml_encode(self, root: etree.Element):
        admf_id = etree.SubElement(root, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(root, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(root, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(root, ns1_ns + VERSION)
        version.text = "v1.6.1"

class SimpleResponse(X1Entity):
    """ for creating or removing tasks or destinations"""
    def __init__(self, admf_id, ne_id, x1_transaction_id, ok, error, code, type_for_error, type):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.ok = ok
        self.error = error
        self.code = code
        self.type_for_error = type_for_error
        self.type = type
    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1ResponseMessage")
        req.attrib[xsi_ns + "type"] = "ns1:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        if self.ok is not None:
            oK = etree.SubElement(req, ns1_ns+"oK")
            oK.text = self.ok
        else:
            req_type = etree.SubElement(req, ns1_ns+REQMESSAGETYPE)
            req_type.text = self.type_for_error
            error = etree.SubElement(req, ns1_ns+ERROR)

            code = etree.SubElement(error, ns1_ns+ERROR_CODE)
            desc = etree.SubElement(error, ns1_ns + ERROR_DESC)
            desc.text = self.error
            code.text = self.code

        return req

class IdentityAssociationRequest(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, observed_time, suci, fiveg_tmsi, fiveg_guti, nr_cell_identity, tracking_area_code):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.observed_time = observed_time
        self.suci = suci
        self.fiveg_tmsi = fiveg_tmsi
        self.fiveg_guti = fiveg_guti
        self.nr_cell_identity = nr_cell_identity
        self.tracking_area_code = tracking_area_code
        self.type = "IdentityAssociationRequest"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1RequestMessage")
        req.attrib[xsi_ns + "type"] = "identity:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        request_details = etree.SubElement(req, identity_ns+"RequestDetails")
        type = etree.SubElement(request_details, identity_ns+"Type")
        owner = etree.SubElement(type, identity_ns+"Owner")
        owner.text = "3GPP"
        name = etree.SubElement(type, identity_ns + "Name")
        name.text = "RequestType"
        value = etree.SubElement(type, identity_ns + "Value")
        value.text = "IdentityAssociation"

        observed_time = etree.SubElement(request_details, identity_ns+"ObservedTime")
        observed_time.text = self.observed_time

        request_values = etree.SubElement(request_details, identity_ns+"RequestValues")

        def format_value(value_t, name_t):
            root = etree.Element(identity_ns+"RequestValue")
            format = etree.SubElement(root, identity_ns+"FormatType")
            owner = etree.SubElement(format, identity_ns+"FormatOwner")
            owner.text = "3GPP"
            name = etree.SubElement(format, identity_ns + "FormatName")
            name.text = name_t
            value = etree.SubElement(root, identity_ns+"Value")
            value.text = value_t
            return root

        if self.suci is not None:
            request_values.append(format_value(self.suci, "SUCI"))

        if self.fiveg_tmsi is not None:
            request_values.append(format_value(self.fiveg_tmsi, "5GSTMSI"))

        if self.fiveg_guti is not None:
            request_values.append(format_value(self.fiveg_guti, "5GGUTI"))

        if self.nr_cell_identity is not None:
            request_values.append(format_value(self.nr_cell_identity, "NRCellIdentity"))

        if self.tracking_area_code is not None:
            request_values.append(format_value(self.tracking_area_code, "TrackingAreaCode"))

        return req

class IdentityAssociationRecord():
    def __init__(self,supi, suci, fiveg_guti, start_time,
                 end_time):
        self.suci = suci
        self.supi = supi
        self.fiveg_guti = fiveg_guti
        self.start_time = start_time
        self.end_time = end_time

    def xml_encode(self):
        root = etree.Element(identity_ns+"IdentityAssociationRecord")
        supi = etree.SubElement(root, identity_ns+"SUPI")
        imsi = etree.SubElement(supi, identity_ns+"SUPIIMSI")
        imsi.text = self.supi

        if self.suci is not None:
            suci = etree.SubElement(root, identity_ns + "SUCI")
            suci.text = self.supi

        guti = etree.SubElement(root, identity_ns+"FiveGGUTI")
        guti.text = self.fiveg_guti

        start = etree.SubElement(root, identity_ns+"AssociationStartTime")
        start.text = self.start_time

        if self.end_time is not None:
            end = etree.SubElement(root, identity_ns + "AssociationEndTime")
            end.text = self.end_time

        return root
class IdentityAssociationResponse(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, records : [IdentityAssociationRecord]):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.records = records
        self.type = "IdentityAssociationResponse"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1ResponseMessage")
        req.attrib[xsi_ns + "type"] = "identity:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        response_details = etree.SubElement(req, identity_ns + "ResponseDetails")
        associations = etree.SubElement(response_details, identity_ns+"Associations")

        for record in self.records:
            associations.append(record.xml_encode())

        return req
class PrivateIdentityAssociationRequest(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, pir_query):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.pir_query = pir_query
        self.type = "PrivateIdentityAssociationRequest"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1RequestMessage")
        req.attrib[xsi_ns + "type"] = "identity:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        request_details = etree.SubElement(req, identity_ns + "PrivateRequestDetails")
        query = etree.SubElement(request_details, identity_ns+"PIRQuery")
        query.text = self.pir_query
        return req

class PrivateIdentityAssociationResponse(X1Entity):
    def __init__(self, admf_id, ne_id, x1_transaction_id, pir_answer):
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_transaction_id = x1_transaction_id
        self.pir_answer = pir_answer
        self.type = "PrivateIdentityAssociationResponse"

    def xml_encode(self):
        req = etree.Element(ns1_ns + "x1ResponseMessage")
        req.attrib[xsi_ns + "type"] = "identity:" + self.type

        admf_id = etree.SubElement(req, ns1_ns + ADMFID)
        admf_id.text = self.admf_id

        ne_id = etree.SubElement(req, ns1_ns + NEID)
        ne_id.text = self.ne_id

        timestamp = etree.SubElement(req, ns1_ns + TIMESTP)
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        version = etree.SubElement(req, ns1_ns + VERSION)
        version.text = "v1.6.1"

        x1_tid = etree.SubElement(req, ns1_ns + X1TID)
        x1_tid.text = self.x1_transaction_id

        response_details = etree.SubElement(req, identity_ns + "PrivateResponseDetails")
        answer = etree.SubElement(response_details, identity_ns + "PIRAnswer")
        answer.text = self.pir_answer

        return req


class X1Message():
    def __init__(self, entity: X1Entity, error: TopLevelErrorResponse=None):
        self.entity = entity
        self.error = error
    def xml_encode(self):
        if "Request" in self.entity.type:
            tag = "X1Request"
            req = etree.Element(ns1_ns + tag, nsmap=NSMAP)
            req.append(self.entity.xml_encode())
        elif self.error is None:
            tag = "X1Response"
            req = etree.Element(ns1_ns + tag, nsmap=NSMAP)
            req.append(self.entity.xml_encode())
        else:
            tag = "X1TopLevelErrorResponse"
            req = etree.Element(ns1_ns + tag, nsmap=NSMAP)
            self.error.xml_encode(req)
        return req
