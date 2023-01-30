from pyli5.iface.x1.x1_messages import *
from pyli5.iface.x1.x1 import *

def test_parsing():
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

def test_encode():
    msg = X1Message(
        entity=ActivateTaskRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            xId="29f28e1c-f230-486a-a860-f5a784ab9172",
            dIds=["19867c20-8c94-473e-b9cd-8b72b7b05fd4"],
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=CreateDestinationRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            dId="29f28e1c-f230-486a-a860-f5a784ab9172",
            address="10.0.0.80",
            port="1234"
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=DeactivateTaskRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            xId="29f28e1c-f230-486a-a860-f5a784ab9172",
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=RemoveDestinationRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            dId="29f28e1c-f230-486a-a860-f5a784ab9172",
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=SimpleResponse(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            ok=OK_ACKnCOMPLETED,
            error=None,
            code=None,
            type_for_error=None,
            type=TYPE_ACTIVATETASK + "Response"
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=SimpleResponse(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            ok=None,
            error="Error",
            code="2001",
            type_for_error="ActivateTask",
            type=TYPE_ERROR + "Response"
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=IdentityAssociationRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            observed_time=get_time_utc(),
            suci="AAAAAAAAAAA",
            fiveg_guti=None,
            fiveg_tmsi=None,
            nr_cell_identity=None,
            tracking_area_code=None
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)

    msg = X1Message(
        entity=IdentityAssociationResponse(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            records=[IdentityAssociationRecord(
                supi="123456789",
                suci="AAAAAAAAAA",
                fiveg_guti="5gguti-8475329759823",
                start_time=get_time_utc(),
                end_time=get_time_utc(),
            )]
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=PrivateIdentityAssociationRequest(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            pir_query=base64.b64encode("AAAAAAAAAAAAAAAAAA".encode())
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

    msg = X1Message(
        entity=PrivateIdentityAssociationResponse(
            admf_id="admfID",
            ne_id="neID",
            x1_transaction_id="3741800e-971b-4aa9-85f4-466d2b1adc7f",
            pir_answer=base64.b64encode("AAAAAAAAAAAAAAAAAA".encode())
        )
    )
    xml = etree.tostring(msg.xml_encode(), xml_declaration=True, pretty_print=True)
    XSD.assertValid(etree.fromstring(xml))

