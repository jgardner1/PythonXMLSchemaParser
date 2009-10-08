#!/usr/bin/env python

from xmlschemaparser import from_wsdl_filename

schema_parser = from_wsdl_filename("AWSECommerceService.wsdl")
result = schema_parser.parse_filename("result.xml")
