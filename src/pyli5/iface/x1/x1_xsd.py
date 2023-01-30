from lxml import etree

import os

XS = 'http://www.w3.org/2001/XMLSchema'
PATH = os.path.dirname(__file__)

def load_schema(xsd):
    with  open(xsd,'r') as xsd_file:
        xsd_doc = etree.parse(xsd_file)

        imports = xsd_doc.xpath('//*/xs:import', namespaces={'xs': XS})
        for ns in imports:
            if 'common' in ns.attrib['namespace']:
                ns.attrib['schemaLocation'] = PATH+"/ts_10322101v011301p0/schema/"+"TS_103_280_01.xsd"
            elif 'HashedID' in ns.attrib['namespace']:
                ns.attrib['schemaLocation'] = PATH + "/ts_10322101v011301p0/schema/" + "TS_103_221_01_HashedID.xsd"
            elif 'Destination' in ns.attrib['namespace']:
                ns.attrib['schemaLocation'] = PATH + "/ts_10322101v011301p0/schema/" + "TS_103_221_01_DestinationSet.xsd"
            elif "3GPP" in ns.attrib['namespace']:
                ns.attrib['schemaLocation'] = PATH + "/ts_10322101v011301p0/schema/" + "3GPPIdentityExtensions_r17_v3.xsd"
            else:
                ns.attrib['schemaLocation'] = PATH + "/ts_10322101v011301p0/schema/" + "TS_103_221_01_v011301.xsd"

        return etree.XMLSchema(xsd_doc)

XSD = load_schema(PATH+"/ts_10322101v011301p0/schema/TS_103_221_01_Validation.xsd")