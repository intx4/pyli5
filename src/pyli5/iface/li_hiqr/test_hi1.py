import logging
from pyli5.iface.li_hiqr.hi1 import *
from pyli5.iface.li_hiqr.hi1_messages import *
import pytest

def test_parsing():
    parser = H1_Parser()
    with open(PATH + "examples/request1.xml", 'r') as f:
        try:
            msg = parser.parse_HI1Message(f.read().encode())
            print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))
        except GenericError as ex:
            print(str(ex))
            pass
    with open(PATH + "examples/response1.xml", 'r') as f:
        msg = parser.parse_HI1Message(f.read().encode())
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "examples/error.xml", 'r') as f:
        msg = parser.parse_HI1Message(f.read().encode())
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "examples/top_level_error.xml", 'r') as f:
        msg = parser.parse_HI1Message(f.read().encode())
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "examples/ldtask.xml", 'r') as f:
        msg = parser.parse_HI1Message(f.read().encode())
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

    with open(PATH + "examples/private_ldtask.xml", 'r') as f:
        msg = parser.parse_HI1Message(f.read().encode())
        print(etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True))

def test_encoding():
    header = Header(HeaderIdentifier("XX", "ACTOR01"), HeaderIdentifier("XX", "ACTOR02"),
                    transactionId="c02358b2-76cf-4ba4-a8eb-f6436ccaea2e")

    payload = Payload(HI1_PAYLOAD_REQUEST, [
        Action(HI1_ACTION_REQUEST, "CREATE", "0", None, Authorisation_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646045",
            auth_reference="W000001",
            start_time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            end_time=(datetime.datetime.now() + datetime.timedelta(days=50)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        )),
        Action(HI1_ACTION_REQUEST, "CREATE", "1", None, LD_Task_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646046",
            associated_objects=["7dbbc880-8750-4d3c-abe7-ea4a17646045"],
            reference="LD-0-0",
            time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            details={
                '5GSTMSI': "AAAAAAAA",
                'NRCellIdentity': "01",
                'TrackingAreaCode': "01",
            },
            delivery_details=Delivery_Details(address="127.0.0.1", port="16000")
        ))
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))

    print("LD TASK OBJ OK\n")

    payload = Payload(HI1_PAYLOAD_REQUEST, [
        Action(HI1_ACTION_REQUEST, "CREATE", "0", None, Authorisation_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646045",
            auth_reference="W000001",
            start_time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            end_time=(datetime.datetime.now() + datetime.timedelta(days=50)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        )),
        Action(HI1_ACTION_REQUEST, "CREATE", "1", None, Private_LD_Task_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646046",
            associated_objects=["7dbbc880-8750-4d3c-abe7-ea4a17646045"],
            reference="LD-0-0",
            query="YWFhYWFhYWFh",
            delivery_details=Delivery_Details(address="127.0.0.1", port="16000")
        ))
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))

    print("PRIVATE LD TASK OBJ OK\n")

    payload = Payload(HI1_PAYLOAD_REQUEST, [
        Action(HI1_ACTION_REQUEST, "DELIVER", "0", "7dbbc880-8750-4d3c-abe7-ea4a17646045", Delivery_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646045",
            associated_objects=["7dbbc880-8750-4d3c-abe7-ea4a17646046"],
            reference="LD-0-0",
            delivery_id="d1079830-8e9a-4731-8fb7-36b9b961eb72",
            data=base64.b64encode("A".encode())
        )),
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(
        etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))

    print("DELIVERY OBJ OK")

    payload = Payload(HI1_PAYLOAD_REQUEST, [
        Action(HI1_ACTION_REQUEST, "CREATE", "0", None, Document_Object(
            object_identifier="7dbbc880-8750-4d3c-abe7-ea4a17646045",
            doc_ref="W0000001",
            start_time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            end_time=(datetime.datetime.now() + datetime.timedelta(days=50)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            approver_name="John Snow",
            approver_email="johnsnow@got.com",
            approver_phone="123456789",
            approval_time=(datetime.datetime.now() + datetime.timedelta(days=-50)).strftime('%Y-%m-%dT%H:%M:%SZ')
        )),
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))

    XSD.assertValid(
        etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))
    print("DOCUMENT OBJ OK\n")

    payload = Payload(HI1_PAYLOAD_RESPONSE, [
        Action(HI1_ACTION_RESPONSE, "CREATEResponse", "0", "7dbbc880-8750-4d3c-abe7-ea4a17646045", None)
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(
        etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))

    print("CREATEResponse OBJ OK")

    payload = Payload(HI1_PAYLOAD_RESPONSE, [
        Action(HI1_ACTION_RESPONSE, "ErrorInformation", "0", None, None, error=ErrorInformation("error", "1000"))
    ])
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(
        etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))

    print("ERROR IN RESPONSE OBJ OK")

    payload = Payload(HI1_PAYLOAD_RESPONSE, None, error=ErrorInformation("error", "1000"))
    message = HI1_Message(header, payload)
    xml = message.xml_encode()
    print(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    XSD.assertValid(
        etree.fromstring(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))
    print("TOP LEVEL ERROR OBJECT OK")