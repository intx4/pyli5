import base64
import datetime
import hashlib
from dataclasses import dataclass
from lxml import etree
from pyli5.iface.li_hiqr.hi1_xsd import XSD

HI1_PAYLOAD_REQUEST = "RequestPayload"
HI1_PAYLOAD_RESPONSE = "ResponsePayload"
HI1_ACTION_REQUEST = "ActionRequest"
HI1_ACTION_RESPONSE = "ActionResponse"

NSMAP={
        None: "http://uri.etsi.org/03120/common/2019/10/Core",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "common": "http://uri.etsi.org/03120/common/2016/02/Common",
        "task": "http://uri.etsi.org/03120/common/2020/09/Task",
        "auth": "http://uri.etsi.org/03120/common/2020/09/Authorisation",
        "delivery": "http://uri.etsi.org/03120/common/2019/10/Delivery",
        "doc": "http://uri.etsi.org/03120/common/2020/09/Document",
        "etsi":"http://uri.etsi.org/03280/common/2017/07"
        }
NSMAPTAG = {}
for k,v in NSMAP.items():
    NSMAPTAG[k] = "{" + v + "}"


class HeaderIdentifier():
    def __init__(self, country_code, unique_identifier):
        self.country_code = country_code
        self.unique_identifier = unique_identifier

    def xml_encode(self, tag):
        root = etree.Element(tag)
        cd = etree.SubElement(root, "CountryCode")
        cd.text = self.country_code
        ui = etree.SubElement(root, "UniqueIdentifier")
        ui.text = self.unique_identifier
        return root


class Header():
    def __init__(self, sender: HeaderIdentifier, receiver: HeaderIdentifier, transactionId: str):
        self.sender = sender
        self.receiver = receiver
        self.transactionId = transactionId
        self.version = "V1.12.1"
        self.national_profile_owner = "XX"
        self.national_profile_version = "v1.0"

    def xml_encode(self):
        root = etree.Element("Header")
        root.append(self.sender.xml_encode("SenderIdentifier"))
        root.append(self.receiver.xml_encode("ReceiverIdentifier"))
        txId = etree.SubElement(root, "TransactionIdentifier")
        txId.text = self.transactionId
        timestamp = etree.SubElement(root, "Timestamp")
        timestamp.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        version = etree.SubElement(root, "Version")
        ETSI_version = etree.SubElement(version, "ETSIVersion")
        ETSI_version.text = self.version
        national_profile_owner = etree.SubElement(version, "NationalProfileOwner")
        national_profile_owner.text = self.national_profile_owner
        national_profile_version = etree.SubElement(version, "NationalProfileVersion")
        national_profile_version.text = self.national_profile_version
        return root


class HI1_Object():
    def __init__(self, object_identifier, associated_objects):
        self.id = object_identifier
        self.associated = associated_objects

    def xml_encode(self):
        pass


class Request_Value():
    def __init__(self, format, value):
        self.format = format
        self.value = value

    def xml_encode(self):
        root = etree.Element(f"{NSMAPTAG['task']}RequestValue", nsmap=NSMAP)
        task_type = etree.SubElement(root, f"{NSMAPTAG['task']}FormatType",nsmap=NSMAP)
        format_owner = etree.SubElement(task_type, f"{NSMAPTAG['task']}FormatOwner",nsmap=NSMAP)
        format_owner.text = "3GPP"
        format_name = etree.SubElement(task_type, f"{NSMAPTAG['task']}FormatName",nsmap=NSMAP)
        format_name.text = self.format
        value = etree.SubElement(root, f"{NSMAPTAG['task']}Value",nsmap=NSMAP)
        value.text = self.value
        return root

class Delivery_Details():
    def __init__(self, address : str, port : str):
        self.address = address
        self.port = port

    def xml_encode(self):
        """
        <task:DeliveryDetails>
                <task:LDDeliveryDestination>
                  <task:DeliveryAddress>
                   <task:IPAddressPort>
                     <etsi:address>
                       <etsi:IPv4Address>127.0.0.1</etsi:IPv4Address>
                     </etsi:address>
                     <etsi:port>
                       <etsi:TCPPort>16000</etsi:TCPPort>
                     </etsi:port>
                   </task:IPAddressPort>
                  </task:DeliveryAddress>
                </task:LDDeliveryDestination>
              </task:DeliveryDetails>
        """
        root = etree.Element(f"{NSMAPTAG['task']}DeliveryDetails", nsmap=NSMAP)
        ld_task_delivery_destination = etree.SubElement(root, f"{NSMAPTAG['task']}LDDeliveryDestination", nsmap=NSMAP)
        delivery_address = etree.SubElement(ld_task_delivery_destination, f"{NSMAPTAG['task']}DeliveryAddress", nsmap=NSMAP)
        ip_addr_port = etree.SubElement(delivery_address, f"{NSMAPTAG['task']}IPAddressPort", nsmap=NSMAP)
        address = etree.SubElement(ip_addr_port, f"{NSMAPTAG['etsi']}address", nsmap=NSMAP)
        ipv4_address = etree.SubElement(address, f"{NSMAPTAG['etsi']}IPv4Address", nsmap=NSMAP)
        ipv4_address.text = self.address
        port = etree.SubElement(ip_addr_port, f"{NSMAPTAG['etsi']}port", nsmap=NSMAP)
        tcp_port = etree.SubElement(port, f"{NSMAPTAG['etsi']}TCPPort", nsmap=NSMAP)
        tcp_port.text = self.port
        return root
class LD_Task_Object(HI1_Object):
    def __init__(self, object_identifier, associated_objects, reference, time, details, delivery_details : Delivery_Details):
        self.object_identifier = object_identifier
        self.associated = associated_objects
        self.reference = reference
        self.time = time
        self.details = details
        self.delivery_details = delivery_details

    def xml_encode(self):
        root = etree.Element("HI1Object", attrib={f"{NSMAPTAG['xsi']}type": "task:LDTaskObject"},nsmap=NSMAP)
        obj_id = etree.SubElement(root, "ObjectIdentifier")
        obj_id.text = self.object_identifier
        cd = etree.SubElement(root, "CountryCode")
        cd.text = "XX"
        oid = etree.SubElement(root, "OwnerIdentifier")
        oid.text = "ACTOR01"
        associated_objects = etree.SubElement(root, "AssociatedObjects")
        for associated in self.associated:
            ass_object = etree.Element("AssociatedObject")
            ass_object.text = associated
            associated_objects.append(ass_object)

        reference = etree.SubElement(root, f"{NSMAPTAG['task']}Reference",nsmap=NSMAP)
        reference.text = self.reference

        desired_status = etree.SubElement(root, f"{NSMAPTAG['task']}DesiredStatus",nsmap=NSMAP)
        owner = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Owner",nsmap=NSMAP)
        owner.text = "3GPP"
        name = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Name",nsmap=NSMAP)
        name.text = "LDTaskStatus"
        value = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Value",nsmap=NSMAP)
        value.text = "AwaitingDisclosure"

        request_details = etree.SubElement(root, f"{NSMAPTAG['task']}RequestDetails",nsmap=NSMAP)
        req_type = etree.SubElement(request_details, f"{NSMAPTAG['task']}Type",nsmap=NSMAP)
        owner = etree.SubElement(req_type, f"{NSMAPTAG['common']}Owner",nsmap=NSMAP)
        owner.text = "3GPP"
        name = etree.SubElement(req_type, f"{NSMAPTAG['common']}Name",nsmap=NSMAP)
        name.text = "RequestType"
        value = etree.SubElement(req_type, f"{NSMAPTAG['common']}Value",nsmap=NSMAP)
        value.text = "IdentityAssociation"

        time = etree.SubElement(request_details, f"{NSMAPTAG['task']}ObservedTime",nsmap=NSMAP)
        time.text = self.time
        request_values = etree.SubElement(request_details, f"{NSMAPTAG['task']}RequestValues",nsmap=NSMAP)
        for format, value in self.details.items():
            request_values.append(Request_Value(format, value).xml_encode())

        root.append(self.delivery_details.xml_encode())
        return root

class Private_LD_Task_Object(HI1_Object):
    def __init__(self, object_identifier, associated_objects, reference, query, delivery_details:Delivery_Details):
        self.object_identifier = object_identifier
        self.associated = associated_objects
        self.reference = reference
        self.query = query
        self.delivery_details = delivery_details

    def xml_encode(self):
        root = etree.Element("HI1Object", attrib={f"{NSMAPTAG['xsi']}type": "task:PrivateLDTaskObject"},nsmap=NSMAP)
        obj_id = etree.SubElement(root, "ObjectIdentifier")
        obj_id.text = self.object_identifier
        cd = etree.SubElement(root, "CountryCode")
        cd.text = "XX"
        oid = etree.SubElement(root, "OwnerIdentifier")
        oid.text = "ACTOR01"
        associated_objects = etree.SubElement(root, "AssociatedObjects")
        for associated in self.associated:
            ass_object = etree.Element("AssociatedObject")
            ass_object.text = associated
            associated_objects.append(ass_object)

        reference = etree.SubElement(root, f"{NSMAPTAG['task']}Reference",nsmap=NSMAP)
        reference.text = self.reference

        desired_status = etree.SubElement(root, f"{NSMAPTAG['task']}DesiredStatus",nsmap=NSMAP)
        owner = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Owner",nsmap=NSMAP)
        owner.text = "3GPP"
        name = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Name",nsmap=NSMAP)
        name.text = "LDTaskStatus"
        value = etree.SubElement(desired_status, f"{NSMAPTAG['common']}Value",nsmap=NSMAP)
        value.text = "AwaitingDisclosure"

        request_details = etree.SubElement(root, f"{NSMAPTAG['task']}PrivateRequestDetails",nsmap=NSMAP)
        req_type = etree.SubElement(request_details, f"{NSMAPTAG['task']}Type", nsmap=NSMAP)
        owner = etree.SubElement(req_type, f"{NSMAPTAG['common']}Owner", nsmap=NSMAP)
        owner.text = "3GPP"
        name = etree.SubElement(req_type, f"{NSMAPTAG['common']}Name", nsmap=NSMAP)
        name.text = "RequestType"
        value = etree.SubElement(req_type, f"{NSMAPTAG['common']}Value", nsmap=NSMAP)
        value.text = "PrivateIdentityAssociation"
        query = etree.SubElement(request_details, f"{NSMAPTAG['task']}PIRQuery")
        query.text = self.query

        root.append(self.delivery_details.xml_encode())

        return root
class Delivery_Object(HI1_Object):
    """
   
    """

    def __init__(self, object_identifier, associated_objects, reference, delivery_id, data):
        self.object_identifier = object_identifier
        self.associated = associated_objects
        self.reference = reference
        self.delivery_id = delivery_id
        if type(data) == str:
            self.data = data.encode()
        elif type(data) == bytes:
            self.data = data

    def xml_encode(self):
        root = etree.Element("HI1Object", attrib={f"{NSMAPTAG['xsi']}type": "delivery:DeliveryObject"},nsmap=NSMAP)
        obj_id = etree.SubElement(root, "ObjectIdentifier")
        obj_id.text = self.object_identifier
        associated_objects = etree.SubElement(root, "AssociatedObjects")
        for associated in self.associated:
            ass_object = etree.Element("AssociatedObject")
            ass_object.text = associated
            associated_objects.append(ass_object)

        reference = etree.SubElement(root, f"{NSMAPTAG['delivery']}Reference",nsmap=NSMAP)
        ldid = etree.SubElement(reference, f"{NSMAPTAG['delivery']}LDID",nsmap=NSMAP)
        ldid.text = self.reference

        delivery_id = etree.SubElement(root, f"{NSMAPTAG['delivery']}DeliveryID",nsmap=NSMAP)
        delivery_id.text = self.delivery_id

        sqn = etree.SubElement(root, f"{NSMAPTAG['delivery']}SequenceNumber",nsmap=NSMAP)
        sqn.text = "1"
        last_seq = etree.SubElement(root, f"{NSMAPTAG['delivery']}LastSequence",nsmap=NSMAP)
        last_seq.text = "true"

        manifest = etree.SubElement(root, f"{NSMAPTAG['delivery']}Manifest",nsmap=NSMAP)
        spec = etree.SubElement(manifest, f"{NSMAPTAG['delivery']}Specification",nsmap=NSMAP)
        owner = etree.SubElement(spec, f"{NSMAPTAG['common']}Owner",nsmap=NSMAP)
        owner.text = "3GPP"
        name = etree.SubElement(spec, f"{NSMAPTAG['common']}Name",nsmap=NSMAP)
        name.text = "ManifestSpecification"
        value = etree.SubElement(spec, f"{NSMAPTAG['common']}Value",nsmap=NSMAP)
        value.text = "LIHIQRResponse"

        delivery = etree.SubElement(root, f"{NSMAPTAG['delivery']}Delivery",nsmap=NSMAP)
        bin_data = etree.SubElement(delivery, f"{NSMAPTAG['delivery']}BinaryData",nsmap=NSMAP)
        data = etree.SubElement(bin_data, f"{NSMAPTAG['delivery']}Data",nsmap=NSMAP)
        data.text = self.data
        ctype = etree.SubElement(bin_data, f"{NSMAPTAG['delivery']}ContentType",nsmap=NSMAP)
        ctype.text = "text"
        checksum = etree.SubElement(bin_data, f"{NSMAPTAG['delivery']}Checksum",nsmap=NSMAP)
        checksum.text = hashlib.sha256(self.data).hexdigest()
        return root

class Authorisation_Object(HI1_Object):
    def __init__(self, object_identifier, auth_reference, start_time, end_time):
        self.object_identifier = object_identifier
        self.auth_reference = auth_reference
        self.start = start_time
        self.end = end_time

    def xml_encode(self):
        root = etree.Element("HI1Object", attrib={f"{NSMAPTAG['xsi']}type": "auth:AuthorisationObject"},nsmap=NSMAP)
        obj_id = etree.SubElement(root, "ObjectIdentifier")
        obj_id.text = self.object_identifier
        cd = etree.SubElement(root, "CountryCode")
        cd.text = "XX"
        oid = etree.SubElement(root, "OwnerIdentifier")
        oid.text = "ACTOR01"

        reference = etree.SubElement(root, f"{NSMAPTAG['auth']}AuthorisationReference",nsmap=NSMAP)
        reference.text = self.auth_reference

        time_span = etree.SubElement(root, f"{NSMAPTAG['auth']}AuthorisationTimespan",nsmap=NSMAP)
        start = etree.SubElement(time_span, f"{NSMAPTAG['auth']}StartTime",nsmap=NSMAP)
        start.text = self.start
        end = etree.SubElement(time_span, f"{NSMAPTAG['auth']}EndTime",nsmap=NSMAP)
        end.text = self.end
        return root

class Document_Object(HI1_Object):
    def __init__(self,object_identifier, doc_ref, start_time, end_time, approver_name, approver_email, approver_phone, approval_time):
        self.object_identifier = object_identifier
        self.doc_ref = doc_ref
        self.start_time = start_time
        self.end_time = end_time
        self.approver = {
            'name': approver_name,
            'email':approver_email,
            'phone':approver_phone,
        }
        self.approval_time = approval_time

    def xml_encode(self):
        root = etree.Element("HI1Object", attrib={f"{NSMAPTAG['xsi']}type": "doc:DocumentObject"},nsmap=NSMAP)
        obj_id = etree.SubElement(root, "ObjectIdentifier")
        obj_id.text = self.object_identifier
        cd = etree.SubElement(root, "CountryCode")
        cd.text = "XX"
        oid = etree.SubElement(root, "OwnerIdentifier")
        oid.text = "ACTOR01"

        reference = etree.SubElement(root, f"{NSMAPTAG['doc']}DocumentReference",nsmap=NSMAP)
        reference.text = self.doc_ref

        time_span = etree.SubElement(root, f"{NSMAPTAG['doc']}DocumentTimespan",nsmap=NSMAP)
        start = etree.SubElement(time_span, f"{NSMAPTAG['doc']}StartTime",nsmap=NSMAP)
        start.text = self.start_time
        end = etree.SubElement(time_span, f"{NSMAPTAG['doc']}EndTime",nsmap=NSMAP)
        end.text = self.end_time

        doc_type = etree.SubElement(root, f"{NSMAPTAG['doc']}DocumentType",nsmap=NSMAP)
        owner = etree.SubElement(doc_type, f"{NSMAPTAG['common']}Owner", nsmap=NSMAP)
        owner.text = "ETSI"
        name = etree.SubElement(doc_type, f"{NSMAPTAG['common']}Name", nsmap=NSMAP)
        name.text = "DocumentType"
        value = etree.SubElement(doc_type, f"{NSMAPTAG['common']}Value", nsmap=NSMAP)
        value.text = "Warrant"

        signature = etree.SubElement(root, f"{NSMAPTAG['doc']}DocumentSignature")
        approver_details = etree.SubElement(signature,f"{NSMAPTAG['common']}ApproverDetails")
        approver_name = etree.SubElement(approver_details, f"{NSMAPTAG['common']}ApproverName")
        approver_name.text = self.approver['name']

        contact_details = etree.SubElement(approver_details, f"{NSMAPTAG['common']}ApproverContactDetails")
        email = etree.SubElement(contact_details,f"{NSMAPTAG['common']}ApproverEmailAddress")
        email.text = self.approver['email']
        phone = etree.SubElement(contact_details, f"{NSMAPTAG['common']}ApproverPhoneNumber")
        phone.text = self.approver['phone']

        app_time = etree.SubElement(signature, f"{NSMAPTAG['common']}ApprovalTimestamp")
        app_time.text = self.approval_time

        return root

class ErrorInformation():
    def __init__(self, desc, code):
        self.desc = desc
        self.code = code

    def xml_encode(self):
        root = etree.Element("ErrorInformation")
        code = etree.SubElement(root, "ErrorCode")
        code.text = self.code
        desc = etree.SubElement(root,"ErrorDescription")
        desc.text = self.desc
        return root
class Action():
    def __init__(self, type, verb, action_identifier, identifier, object: HI1_Object, error: ErrorInformation=None):
        self.type = type
        self.verb = verb
        self.action_identifier = action_identifier
        self.identifier = identifier
        self.object = object
        self.error = error

    def xml_encode(self):
        root = etree.Element(self.type)
        identifier = etree.SubElement(root, "ActionIdentifier")
        identifier.text = self.action_identifier
        if self.error is None:
            verb = etree.SubElement(root, self.verb)
            if self.identifier is not None:
                identifier = etree.SubElement(verb, "Identifier")
                identifier.text = self.identifier
            if self.object is not None:
                verb.append(self.object.xml_encode())
        else:
            root.append(self.error.xml_encode())
        return root


class Payload():
    def __init__(self, type, actions: [Action], error: ErrorInformation=None):
        self.type = type
        self.actions = actions
        self.error = error

    def xml_encode(self):
        root = etree.Element("Payload")
        payload = etree.SubElement(root, self.type)
        if self.type == HI1_PAYLOAD_REQUEST:
            actions = etree.SubElement(payload, "ActionRequests")
        elif self.type == HI1_PAYLOAD_RESPONSE:
            if self.error is None:
                actions = etree.SubElement(payload, "ActionResponses")
            else:
                payload.append(self.error.xml_encode())
        else:
            raise Exception("Wrong Payload Type")
        if self.actions is not None:
            for action in self.actions:
                actions.append(action.xml_encode())
        return root


class HI1_Message():
    def __init__(self, header: Header, payload: Payload):
        self.header = header
        self.payload = payload

    def xml_encode(self):
        root = etree.Element("HI1Message", nsmap=NSMAP)
        root.append(self.header.xml_encode())
        root.append(self.payload.xml_encode())
        return root




