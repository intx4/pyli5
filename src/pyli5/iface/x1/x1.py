from lxml import etree
from pyli5.iface.x1.x1_xsd import XSD, PATH
from pyli5.iface.x1.x1_messages import *
from pyli5.iface.x1.x1_errors import *
NSMAP={
    "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "x1":"http://uri.etsi.org/03221/X1/2017/10",
    "etsi103280":"http://uri.etsi.org/03280/common/2017/07",
    "hashedID":"http://uri.etsi.org/03221/X1/2017/10/HashedID",
    "destinationSet":"http://uri.etsi.org/03221/X1/2017/10/DestinationSet",
    "identity":"urn:3GPP:ns:li:3GPPIdentityExtensions:r17:v3",
}
NSMAPTAG = {}
for k,v in NSMAP.items():
    NSMAPTAG[k] = "{" + v + "}"

import re

def extract_type(input_string):
    pattern = re.compile(r"[a-zA-Z0-9]*:(.*)")
    match = pattern.search(input_string)
    if match:
        return match.group(1)
    return input_string

class X1Parser():

    def parse_X1_Message(self, data: bytes)->X1Message:
        """
            <ns1:admfIdentifier>admfID</ns1:admfIdentifier>
            <ns1:neIdentifier>neID</ns1:neIdentifier>
            <ns1:messageTimestamp>2017-10-06T18:46:21.247432Z</ns1:messageTimestamp>
            <ns1:version>v1.6.1</ns1:version>
            <ns1:x1TransactionId>3741800e-971b-4aa9-85f4-466d2b1adc7f</ns1:x1TransactionId>
        """
        p = etree.XMLParser(huge_tree=True)
        xml = etree.fromstring(data, parser=p)
        ne_id = ""
        admf_id = ""
        try:
            ne_id = xml.find(".//{*}neIdentifier").text
            admf_id = xml.find(".//{*}admfIdentifier").text
            XSD.assertValid(xml)
        except Exception as ex:
            raise X1MessageError(str(ex), type_for_error="TopLevel", admf_id=admf_id, ne_id=ne_id, code=1010)

        ne_id = xml.find(".//{*}neIdentifier").text
        admf_id = xml.find(".//{*}admfIdentifier").text
        x1_transaction_id = xml.find(".//{*}x1TransactionId").text

        try:
            request = xml.find(".//{*}x1RequestMessage")
            if request is not None:
                request = self._parse_request(request)
                request.admf_id = admf_id
                request.ne_id = ne_id
                request.x1_transaction_id = x1_transaction_id
                return X1Message(request)

            response = xml.find(".//{*}x1ResponseMessage")
            if response is not None:
                response = self._parse_response(response)
                response.admf_id = admf_id
                response.ne_id = ne_id
                response.x1_transaction_id = x1_transaction_id
                return X1Message(response)
        except X1TaskNotSupported as ex:
            raise X1MessageError(str(ex), type_for_error=ex.type_for_error, admf_id=admf_id, ne_id=ne_id, x1_tid=x1_transaction_id,code=1000)

    def _parse_request(self, request)->X1Entity:
        type = extract_type(request.attrib[NSMAPTAG['xsi']+"type"])
        if "ActivateTask" in type:
            task = request.find(".//{*}taskDetails")
            try:
                task = self._parse_task(task)
            except X1TaskNotSupported as ex:
                ex.type_for_error="ActivateTask"
                raise ex
            return task
        elif "DeactivateTask" in type:
            xid = request.find(".//{*}xId").text
            return DeactivateTaskRequest(None, None, None, xId = xid)
        elif "CreateDestination" in type:
            destination = request.find(".//{*}destinationDetails")
            destination = self._parse_destination(destination)
            return destination
        elif "RemoveDestination" in type:
            did = request.find(".//{*}dId").text
            return RemoveDestinationRequest(None, None, None, dId = did)
        elif "PrivateIdentityAssociation" in type:
            return self._parse_private_identity_association_request(request.find(".//{*}PrivateRequestDetails"))
        elif "IdentityAssociation" in type:
            return self._parse_identity_association_request(request.find(".//{*}RequestDetails"))


    def _parse_identity_association_request(self, req):
        observed_time = req.find(".//{*}ObservedTime").text
        association_req = IdentityAssociationRequest(None, None, None, observed_time, None, None, None,None, None)
        for value in req.findall(".//{*}RequestValue"):
            format = value.find(".//{*}FormatName").text
            value = value.find(".//{*}Value").text
            if format == "SUCI":
                association_req.suci = value
            elif format == "5GSTMSI":
                association_req.fiveg_tmsi = value
            elif format == "5GGUTI":
                association_req.fiveg_guti = value
            elif format == "NRCellIdentity":
                association_req.nr_cell_identity = value
            elif format == "TrackingAreaCode":
                association_req.tracking_area_code = value
        return association_req

    def _parse_private_identity_association_request(self, req):
        query = req.find(".//{*}PIRQuery").text
        association_req = PrivateIdentityAssociationRequest(None, None, None, query)

        return association_req
    def _parse_task(self, task)->X1Entity:
        if task.find(".//{*}targetIdentifiers/{*}targetIdentifier/{*}targetIdentifierExtension/{*}IdentityAssociationTargetIdentifier") is None:
            raise X1TaskNotSupported(info="Check targetIdentifiers only contains empty extension IdentityAssociationTargetIdentifier")
        if task.find(".//{*}deliveryType").text != "X2Only":
            raise X1TaskNotSupported(info="deliveryType must be X2Only")
        dids = [o.text for o in task.findall(".//{*}dId")]
        xid = task.find(".//{*}xId").text
        return ActivateTaskRequest(None, None, None, xId=xid, dIds = dids)

    def _parse_destination(self, destination)->X1Entity:
        did = destination.find(".//{*}dId").text
        addr = destination.find(".//{*}IPv4Address").text
        port = destination.find(".//{*}TCPPort").text
        return CreateDestinationRequest(None, None, None, dId=did, address=addr, port=port)

    def _parse_response(self, response)->X1Entity:
        type = extract_type(response.attrib[NSMAPTAG['xsi'] + "type"])
        if "ActivateTask" in type or "DeactivateTask" in type or "CreateDestination" in type or "RemoveDestination" in type:
            ok = response.find(".//{*}oK")
            if ok is not None:
                ok = ok.text
                return SimpleResponse(None, None, None, ok, None, None, None, type=type)
            else:
                error = response.find(".//{*}ErrorInformation")
                description = error.find(".//{*}ErrorDescription")
                code = error.find(".//{*}ErrorCode")
                type_for_error = ""
                if "ActivateTask" in type:
                    type_for_error = "ActivateTask"
                elif "DeactivateTask" in type:
                    type_for_error = "DeactivateTask"
                elif "CreateDestination" in type:
                    type_for_error = "CreateDestination"
                elif "RemoveDestination" in type:
                    type_for_error = "RemoveDestination"
            return SimpleResponse(None, None, None, None, description, code, type_for_error=type_for_error, type=type)
        elif "PrivateIdentityAssociation" in type:
            return self._parse_private_identity_association_response(response.find(".//{*}PrivateResponseDetails"))
        elif "IdentityAssociation" in type:
            return self._parse_identity_association_response(response.find(".//{*}ResponseDetails"))

    def _parse_identity_association_response(self, response):
        association_response = IdentityAssociationResponse(None, None, None, [])
        for record in response.findall(".//{*}IdentityAssociationRecord"):
            association_record = IdentityAssociationRecord(None, None, None, None, None)
            if record.find(".//{*}SUPIIMSI") is not None:
                association_record.supi = record.find(".//{*}SUPIIMSI").text
            if record.find(".//{*}SUCI") is not None:
                association_record.suci = record.find(".//{*}SUCI").text
            if record.find(".//{*}FiveGGUTI") is not None:
                association_record.fiveg_guti = record.find(".//{*}FiveGGUTI").text
            if record.find(".//{*}AssociationStartTime") is not None:
                association_record.start_time = record.find(".//{*}AssociationStartTime").text
            if record.find(".//{*}AssociationEndTime") is not None:
                association_record.end = record.find(".//{*}AssociationEndTime").text
            association_response.records.append(association_record)
        return association_response
    def _parse_private_identity_association_response(self, response):
        return PrivateIdentityAssociationResponse(None, None, None, response.find(".//{*}PIRAnswer").text)

if __name__ == "__main__":
    with open(PATH+"/ts_10322101v011301p0/examples/ActivateTaskRequest_LIHIQR.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))
    with open(PATH+"/ts_10322101v011301p0/examples/CreateDestinationRequest_example.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))
    with open(PATH + "/ts_10322101v011301p0/examples/IdentityAssociationRequest_example.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "/ts_10322101v011301p0/examples/IdentityAssociationResponse_example.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "/ts_10322101v011301p0/examples/PrivateIdentityAssociationRequest_example.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "/ts_10322101v011301p0/examples/PrivateIdentityAssociationResponse_example.xml") as f:
        data = f.read()
        xml = etree.fromstring(data)
        XSD.assertValid(xml)
        parser = X1Parser()
        msg = parser.parse_X1_Message(data)
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

