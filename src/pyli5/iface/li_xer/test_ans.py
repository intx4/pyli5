from pyli5.iface.li_xer.pyasn import *

def test_asn():
    record = iefRecord(
        assoc=iefAssociationRecord(
            supi="123456789",
            suci="AAAAAAAAAAAA",
            fivegguti="0102030405",
            timestmp=get_time_utc(),
            tai="010101",
            pei="4370816125816151",
            ncgi={"nCI": bin(int("0x10", 16))[2:].zfill(36), "pLMNID":"999"},
            ncgi_time=get_time_utc(),
            list_of_tai=["010101","101010"]
        ),
        deassoc=None
    )
    ber = encode(record)
    print(base64.b64encode(ber))
    msg = decode(ber)
    url = "http://127.0.0.1:6021"
    headers = {"Content-Length": str(len(base64.b64encode(ber)))}
    response = requests.post(url, data=base64.b64encode(ber), headers=headers)
    print(response.text)
    time.sleep(1)
    record = iefRecord(
        assoc=None,
        deassoc=iefDeassociationRecord(
            supi="123456789",
            suci="AAAAAAAAAAAA",
            fivegguti="0102030405",
            timestmp=get_time_utc(),
            ncgi={"nCI": bin(int("0x10", 16))[2:].zfill(36), "pLMNID": "999"},
            ncgi_time=get_time_utc(),
        ),
    )
    ber = encode(record)
    print(base64.b64encode(ber))
    msg = decode(ber)
    print(msg)
    headers = {"Content-Length": str(len(base64.b64encode(ber)))}
    response = requests.post(url, data=base64.b64encode(ber), headers=headers)
    print(response.text)