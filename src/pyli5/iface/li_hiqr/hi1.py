from pyli5.utils.logger import Logger

import os
import logging
from queue import Queue
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.iface.li_hiqr.hi1_xsd import XSD
from pyli5.iface.li_hiqr.hi1_errors import *

XS = 'http://www.w3.org/2001/XMLSchema'
PATH = os.path.dirname(__file__)+"/ts_103120v011201p0/"

class H1_Parser():
    def _parse_header_identifer(self,Id):
        countryCode = Id[0].text
        uniqueId = Id[1].text

        return HeaderIdentifier(country_code=countryCode, unique_identifier=uniqueId)

    def _parse_header(self,header):
        senderId = self._parse_header_identifer(header.find(".//{*}SenderIdentifier"))
        receiverId = self._parse_header_identifer(header.find(".//{*}ReceiverIdentifier"))
        trxId = header.find(".//{*}TransactionIdentifier").text
        return Header(senderId, receiverId, trxId)

    def _parse_action(self,action):
        error = None
        action_identifier = action.find(".//{*}ActionIdentifier").text
        action = action.getchildren()[1]
        if "Response" in action.tag:
            if "CREATE" in action.tag:
                #object
                identifier = action.find(".//{*}Identifier").text
            elif "GET" in action.tag:
                raise NotImplementedError(action.tag)
            elif "UPDATE" in action.tag:
                raise NotImplementedError(action.tag)
            elif "LIST" in action.tag:
                raise NotImplementedError(action.tag)
            elif "DELIVER" in action.tag:
                identifier = action.find(".//{*}Identifier").text
                action_identifier = action.find(".//{*}ActionIdentifier").text
            return Action(HI1_ACTION_RESPONSE, action.tag, action_identifier, identifier, None, error)
        elif "ErrorInformation" not in action.tag:
            if "CREATE" in action.tag:
                #object
                object = action.find(".//{*}HI1Object")
                object = self._parse_HI1Object(object)
                identifier = None
            elif "GET" in action.tag:
                raise NotImplementedError(action.tag)
            elif "UPDATE" in action.tag:
                raise NotImplementedError(action.tag)
            elif "LIST" in action.tag:
                raise NotImplementedError(action.tag)
            elif "DELIVER" in action.tag:
                identifier = action.find(".//{*}Identifier").text
                object = action.find(".//{*}HI1Object")
                assert identifier == object.find(".//{*}ObjectIdentifier").text
                object = self._parse_HI1Object(object)
            return Action(HI1_ACTION_REQUEST, action.tag, action_identifier, identifier, object)
        else:
            error_code = action.find(".//{*}ErrorCode").text
            error_desc = action.find(".//{*}ErrorDescription").text
            error = ErrorInformation(error_desc, error_code)
            return Action(HI1_ACTION_RESPONSE, action.tag, action_identifier, None, None, ErrorInformation(error_desc, error_code))


    def _parse_task_request_values(self,request_values):
        values = {}
        for req in request_values:
            format = req.find(".//{*}FormatName").text
            value = req.find(".//{*}Value").text
            values[format] = value

        if "5GSTMSI" in values.keys() or "5GGUTI" in values.keys():
            try:
                assert "NRCellIdentity" in values.keys()
                assert "TrackingAreaCode" in values.keys()
            except AssertionError as ex:
                raise FormatError("LDTaskObject with TMSI or GUTI expects NRCellIdentity and TAC: "+str(ex))
        return values

    def _parse_HI1Object(self,object)->HI1_Object:
        """

        :param object:
        :return: HI!_Object
        """
        obj_id = object.find(".//{*}ObjectIdentifier").text

        if "Authorisation" in object.attrib.values()[0]:
            start_time = object.find(".//{*}StartTime").text
            end_time = object.find(".//{*}EndTime").text
            return Authorisation_Object(obj_id, object.find(".//{*}AuthorisationReference").text,start_time, end_time)

        if "LITaskObject" in object.attrib.values()[0]:
            raise NotImplementedError(info=object.attrib.values()[0])

        if "PrivateLDTaskObject" in object.attrib.values()[0]:
            associatedObjects = [o.text for o in object.findall(".//{*}AssociatedObject")]
            ldid = object.find(".//{*}Reference").text
            if object.find(".//{*}DesiredStatus/{*}Value").text != "AwaitingDisclosure":
                raise NotImplementedError(info=object.find(".//{*}DesiredStatus/{*}Value").text)
            if object.find(".//{*}PrivateRequestDetails/{*}Type/{*}Value").text != "PrivateIdentityAssociation":
                raise NotImplementedError(info=object.find(".//{*}PrivateRequestDetails/{*}Type/{*}Value").text)
            query = object.find(".//{*}PIRQuery").text
            delivery_address = object.find(".//{*}IPv4Address").text
            delivery_port = object.find(".//{*}TCPPort").text
            return Private_LD_Task_Object(obj_id, associatedObjects, ldid, query,Delivery_Details(delivery_address, delivery_port))

        if "LDTaskObject" in object.attrib.values()[0]:
            associatedObjects = [o.text for o in object.findall(".//{*}AssociatedObject")]
            ldid = object.find(".//{*}Reference").text
            if object.find(".//{*}DesiredStatus/{*}Value").text != "AwaitingDisclosure":
                raise NotImplementedError(info=object.find(".//{*}DesiredStatus/{*}Value").text)
            if object.find(".//{*}RequestDetails/{*}Type/{*}Value").text != "IdentityAssociation":
                raise NotImplementedError(info=object.find(".//{*}PrivateRequestDetails/{*}Type/{*}Value").text)
            observed_time = object.find(".//{*}RequestDetails/{*}ObservedTime").text
            request_values = self._parse_task_request_values(object.findall(".//{*}RequestValue"))
            delivery_address = object.find(".//{*}IPv4Address").text
            delivery_port = object.find(".//{*}TCPPort").text
            return LD_Task_Object(obj_id, associatedObjects,ldid, observed_time, request_values, Delivery_Details(delivery_address, delivery_port))


        if "DeliveryObject" in object.attrib.values()[0]:
            associatedObjects = [o.text for o in object.findall(".//{*}AssociatedObject")]
            ldid = object.find(".//{*}Reference/{*}LDID").text
            delivery_id = object.find(".//{*}DeliveryID").text
            data = object.find(".//{*}Delivery/{*}BinaryData/{*}Data").text #base64
            checksum = object.find(".//{*}Delivery/{*}BinaryData/{*}Checksum").text
            try:
                assert hashlib.sha256(data.encode()).hexdigest() == checksum
            except AssertionError as ex:
                raise ChecksumError(info=str(ex))
            return Delivery_Object(obj_id, associatedObjects, ldid, delivery_id, data)

        if "DocumentObject" in object.attrib.values()[0]:
            doc_ref = object.find(".//{*}DocumentReference").text
            start_time = object.find(".//{*}DocumentTimespan/{*}StartTime").text
            end_time = object.find(".//{*}DocumentTimespan/{*}EndTime").text
            signature = object.find(".//{*}DocumentSignature")
            approver_name = signature.find(".//{*}ApproverName").text
            approver_email = signature.find(".//{*}ApproverEmailAddress").text
            approver_phone = signature.find(".//{*}ApproverPhoneNumber").text
            approval_time = signature.find(".//{*}ApprovalTimestamp").text

            return Document_Object(obj_id, doc_ref, start_time, end_time, approver_name, approver_email, approver_phone, approval_time)


    def _parse_payload(self,payload):
        actions = payload[0]
        hi1_actions = []
        if "ActionRequests" in actions.tag:
            for request in actions.getchildren():
                hi1_actions.append(self._parse_action(request))
            return Payload(HI1_PAYLOAD_REQUEST, hi1_actions)
        if "ActionResponses" in actions.tag:
            for response in actions.getchildren():
                hi1_actions.append(self._parse_action(response))
            return Payload(HI1_PAYLOAD_RESPONSE, hi1_actions)
        if "ErrorInformation" in actions.tag:
            error_code = payload.find(".//{*}ErrorCode").text
            error_desc = payload.find(".//{*}ErrorDescription").text
            error = ErrorInformation(error_desc, error_code)
            return Payload(HI1_PAYLOAD_RESPONSE, None, ErrorInformation(error_desc, error_code))


    def parse_HI1Message(self,data : bytes):
        # message is Header + Payload
        msg = etree.fromstring(data)
        try:
            XSD.assertValid(msg)
        except Exception as ex:
            header = msg[0]
            header = self._parse_header(header)
            raise XMLError(header, str(ex))
        header = msg[0]
        payload = msg[1][0]

        #parse header
        header = self._parse_header(header)
        #parse payload
        try:
            payload = self._parse_payload(payload)
        except Exception as ex:
            try:
                ex.header = header
                raise ex
            except:
                # all not custom h1 errors
                generic = GenericError(str(ex))
                generic.header = header
                raise generic
        return HI1_Message(header, payload)


