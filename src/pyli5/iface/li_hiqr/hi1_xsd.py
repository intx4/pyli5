from lxml import etree
import os

XS = 'http://www.w3.org/2001/XMLSchema'
PATH = os.path.dirname(__file__)+"/ts_103120v011201p0/"

def load_schema():
    suffix ='Validation'
    with open(PATH+"schema/"+"ts_103120_"+suffix+".xsd",'r') as xsd_file:
        xsd_doc = etree.parse(xsd_file)
        return etree.XMLSchema(xsd_doc)

XSD = load_schema()