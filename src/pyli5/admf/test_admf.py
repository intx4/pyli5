import time
import requests

from pyli5.iface.li_hiqr import *
from pyli5.iface.x1 import *
from pyli5.iface.li_xqr import *
from pyli5.iface.li_hiqr.hi1_messages import *
from pyli5.admf.licf import LICF
from pyli5.admf.lipf import LIPF, IEFInfo, ICFInfo
from pyli5.admf.iqf import IQF
from pyli5.icf.icf import ICF
from pyli5.lea.lea import LEA
from queue import Queue


def test_LICF_to_LIPF():
    li_admf = Queue()
    licf = LICF("127.0.0.1", "4001", li_admf)
    lipf = LIPF("ADMFID", ief_info=IEFInfo(xem_addr="127.0.01", xem_port="5011", xem_url="/NE", xem_id="NEID"), icf_info=ICFInfo(xer_addr="127.0.0.1", xer_port="6021"), li_admf=li_admf)

    header = Header(HeaderIdentifier("XX","ACTOR01"), HeaderIdentifier("XX","ACTOR02"), transactionId="c02358b2-76cf-4ba4-a8eb-f6436ccaea2e")
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
    response = requests.post(url="http://127.0.0.1:4001",data=etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True), headers={"Content-Length":str(len(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))})

    print("\n\n\nRESPONSE:\n\n\n")
    print(response.text)

    while True:
       pass # for memory efficiency


from pyli5.ief.ief import IEF

def test_LICF_to_LIPF_IEF():
    li_admf = Queue()
    licf = LICF("127.0.0.1", "4001", li_admf)
    lipf = LIPF("ADMFID", ief_info=IEFInfo(xem_addr="172.17.0.1", xem_port="50011", xem_url="/X1/AMF", xem_id="NEID"), icf_info=ICFInfo(xer_addr="172.17.0.1", xer_port="60021"), li_admf=li_admf)
    #ief = IEF(config="/home/intx/PycharmProjects/pyli5/pyli5/ief/config/ief.json")

    header = Header(HeaderIdentifier("XX","ACTOR01"), HeaderIdentifier("XX","ACTOR02"), transactionId="c02358b2-76cf-4ba4-a8eb-f6436ccaea2e")
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
    response = requests.post(url="http://127.0.0.1:4001",data=etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True), headers={"Content-Length":str(len(etree.tostring(xml, xml_declaration=True, encoding="UTF-8", pretty_print=True)))})

    print("\n\n\nRESPONSE:\n\n\n")
    print(response.text)

    while True:
        pass # more efficient


def test_LEA_to_IQF_to_ICF():
    iqf = IQF("AMDF_ID","127.0.0.1","10000", "127.0.0.1","20000")
    icf = ICF("127.0.0.1", "20000")
    lea = LEA("127.0.0.1","30000", "127.0.0.1","10000")
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
            delivery_details=Delivery_Details(address="127.0.0.1", port="30000")
        ))
    ])
    message = HI1_Message(header, payload)
    lea.send(message)

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
            reference="LD-0-1",
            query="YWFhYWFhYWFh",
            delivery_details=Delivery_Details(address="127.0.0.1", port="30000")
        ))
    ])
    message = HI1_Message(header, payload)
    lea.send(message)

    while True:
        pass
