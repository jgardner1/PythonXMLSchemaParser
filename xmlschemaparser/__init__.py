#!/usr/bin/env python

__ALL__ = [
    'from_wsdl_filename',
    'from_wsdl_file',
    'from_schema_filename',
    'from_schema_file',
]

from Parser import parse_xml_filename, parse_xml_file

from XMLSchemaParser import XMLSchemaParser

def from_wsdl_file(wsdl_file):
    wsdl_root, = parse_xml_file(wsdl_file).children
    return from_wsdl_element(wsdl_root)

def from_wsdl_filename(wsdl_file):
    wsdl_root, = parse_xml_filename(wsdl_file).children
    return from_wsdl_element(wsdl_root)

def from_wsdl_element(wsdl_element):
    types, = wsdl_element.findall(XMLSchemaParser.wsdl_uri, "types")
    schema, = types.findall(XMLSchemaParser.xml_schema_uri, "schema")
    return XMLSchemaParser(schema)

def from_schema_file(schema_file):
    schema_root, = parse_xml_file(schema_file).children
    return from_schema_element(schema_root)

def from_schema_filename(schema_file):
    schema_root, = parse_xml_filename(schema_file).children
    return from_schema_element(schema_root)

def from_schema_element(schema_element):
    return XMLSchemaParser(schema)

