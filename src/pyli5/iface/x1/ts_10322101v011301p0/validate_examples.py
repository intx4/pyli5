import glob
import sys
from pathlib import Path


XS = 'http://www.w3.org/2001/XMLSchema'


def validate_example(example, schema):

    print('Validating example {}'.format(example))

    xml = open(example)
    doc = etree.parse(xml)
    schema.assertValid(doc)

    print('Validated example {}'.format(example))


def validate_examples(schema):

    examples = glob.glob('./examples/*.xml')

    if not examples:
        sys.exit('ERROR: No examples found in ./examples/ directory')

    for example in examples:
        validate_example(example, schema)


def load_schema(xsd):

    xsd_file = open(xsd)

    xsd_doc = etree.parse(xsd_file)

    # Set schemaLocation of TS 103 280 XSD

    common_xsd = glob.glob('./TS_103_280_*.xsd')

    if not common_xsd:
        sys.exit('ERROR: Please copy a TS 103 280 XSD into this directory')

    if len(common_xsd) > 1:
        sys.exit('ERROR: Too many TS 103 280 XSDs in current directory')

    imports = xsd_doc.xpath('//*/xs:import', namespaces={'xs': XS})

    for xsd_import in imports:
        xsd_import.attrib['schemaLocation'] = str(Path(common_xsd[0]))
        print (xsd_import.attrib)

    # Load TS 103 221-1 XSD as a schema

    return etree.XMLSchema(xsd_doc)


def validate_xsd(xsd):

    print('Validating XSD {}'.format(xsd))

    schema = load_schema(xsd)

    print('Validated XSD {}'.format(xsd))
    print('')

    validate_examples(schema)

    print('')
    print('Validated all examples for XSD {}'.format(xsd))
    print('')


def validate_xsds():

    xsds = glob.glob('./TS_103_221_01_*.xsd')

    if not xsds:
        sys.exit('ERROR: No TS 103 221-1 XSDs found in current directory')

    for xsd in xsds:
        validate_xsd(xsd)


if __name__ == '__main__':

    if sys.version_info <= (3, 5):
        sys.exit('ERROR: You need at least Python 3.5 to run this tool')

    try:
        from lxml import etree
    except ImportError:
        sys.exit('ERROR: You need to install the Python lxml library')

    validate_xsds()
