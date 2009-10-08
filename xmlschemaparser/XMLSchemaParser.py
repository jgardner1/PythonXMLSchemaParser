#!/usr/bin/env python

"""The XMLSchemaParser."""

__ALL__ = [
    'XMLSchemaParser'
]

from Parser import parse_xml_filename, parse_xml_file
import decimal
import re
import base64


def builtin_boolean(value):
    if value in (u'true', u'1'): return True
    elif value in (u'false', u'0'): return False
    else: raise ValueError("%r is not a boolean" % (value,))

def builtin_duration(value):
    match = re.match('''
        ^
        (?P<sign>-)? # Optional minus sign
        P
        (?:(?P<years>\d{4,})Y)?
        (?:(?P<months>\d+)M)?
        (?:(?P<days>\d+)D)?
        (?:T
            (?:(?P<hours>\d+)H)?
            (?:(?P<minutes>\d+)M)?
            (?:(?P<seconds>\d+(?:.\d+)?)S)?
        )
        $''', value, re.VERBOSE)
    if not match:
        raise ValueError("Invalid duration: %r" % value)

    result = match.groupdict('0')
    for key in ('years', 'months', 'days', 'hours', 'minutes'):
        result[key] = int(result[key])

    result['seconds'] = decimal.Decimal(result['seconds'])
    if result['sign'] != '-':
        result['sign'] = '+'
    
    return result

def builtin_dateTime(value):
    match = re.match('''
        ^
        (?P<year>-?\d{4})
        -
        (?P<month>\d{2})
        -
        (?P<day>\d{2})
        T
        (?P<hour>\d{2})
        :
        (?P<minute>\d{2})
        :
        (?P<second>\d{2}(?:\.\d+)?)
        (?:
            (?P<timezone_sign>[-+])
            (?P<timezone_hour>\d{2})
            :
            (?P<timezone_minute>\d{2})
            |
            (?P<timezone_z>Z))?
        $''', value, re.VERBOSE)
    if not match:
        raise ValueError("Invalid dateTime: %r" % value)

    return dict(
        year = int(match.group('year')),
        month = int(match.group('month')),
        day = int(match.group('day')),
        hour = int(match.group('hour')),
        minute = int(match.group('minute')),
        second = decimal.Decimal(match.group('second')),
        timezone_sign = match.group('timezone_sign'),
        timezone_hour = int(match.group('timezone_hour')),
        timezone_minute = int(match.group('timezone_minute')),
        timezone_z = match.group('timezone_z'))

def builtin_time(value):
    raise NotImplementedError()

def builtin_date(value):
    raise NotImplementedError()

def builtin_gYearMonth(value):
    raise NotImplementedError()

def builtin_gYear(value):
    raise NotImplementedError()

def builtin_gMonthDay(value):
    raise NotImplementedError()

def builtin_gDay(value):
    raise NotImplementedError()

def builtin_gMonth(value):
    raise NotImplementedError()

def builtin_gDay(value):
    raise NotImplementedError()

def builtin_integer_with_range(constraint):
    def _(value):
        int_value = int(value)
        if not constraint(int_value):
            raise ValueError("Invalid value: %r" % value)
        return int_value
    return _


class XMLSchemaParser(object):
    xml_schema_uri = "http://www.w3.org/2001/XMLSchema"
    wsdl_uri = "http://schemas.xmlsoap.org/wsdl/"
    builtin_simple_types = {
        'string':unicode,
        'boolean':builtin_boolean,
        'decimal':decimal.Decimal,
        'float':float,
        'double':float,
        'duration':builtin_duration,
        'dateTime':builtin_dateTime,
        'time':builtin_time,
        'date':builtin_date,
        'gYearMonth':builtin_gYearMonth,
        'gYear':builtin_gYear,
        'gMonthDay':builtin_gMonthDay,
        'gDay':builtin_gDay,
        'gMonth':builtin_gMonth,
        'hexBinary':lambda value: int(value, 16),
        'base64Binary':base64.b64decode,
        'anyURI': unicode,
        'QName': None, # Treat this special

        'integer': int,

        'long': builtin_integer_with_range(
            lambda value: -9223372036854775808 <= value <= 9223372036854775807),
        'unsignedLong': builtin_integer_with_range(
            lambda value: 0 <= value <= 18446744073709551615),
        'int': builtin_integer_with_range(
            lambda value: -2147483648 <= value <= 2147483647),
        'unsignedInt': builtin_integer_with_range(
            lambda value: 0 <= value <= 4294967295),
        'short': builtin_integer_with_range(
            lambda value: -32768 <= value <= 32767),
        'unsignedShort': builtin_integer_with_range(
            lambda value: 0 <= value <= 65535),
        'byte': builtin_integer_with_range(
            lambda value: -128 <= value <= 127),
        'unsignedByte': builtin_integer_with_range(
            lambda value: 0 <= value <= 255),

        'nonPositiveInteger': builtin_integer_with_range(
            lambda value: value <= 0),
        'negativeInteger': builtin_integer_with_range(
            lambda value: value < 0),
        'nonNegativeInteger': builtin_integer_with_range(
            lambda value: value >= 0),
        'positiveInteger': builtin_integer_with_range(
            lambda value: value > 0),

    }

    def __init__(self, schema):
        """Initialize the object given a schema, which is an Element."""
        self.schema = schema

        self.targetNamespace = schema.attr['targetNamespace']

        def make_lookup_dict(type_):
            return dict((
                ((elem.attr.get('targetNamespace', self.targetNamespace),
                    elem.attr['name']), elem)
                for elem in schema.findall(self.xml_schema_uri, type_)))

        self.elements = make_lookup_dict('element')
        self.simpleTypes = make_lookup_dict('simpleType')
        self.complexTypes = make_lookup_dict('complexType')


    def find_global_element_by_element(self, element):
        """Given an actual data element, find the global schema element."""
        return self.find_global_element_by_name(*element.fullname)

    def find_global_element_by_ref(self, ref):
        """Given a ref, find the global schema element."""

        return self.find_global_element_by_name(ref)

    def find_global_element_by_name(self, namespace_uri, name):
        """Given the tag, find the global element matching it."""
        return self.elements[namespace_uri, name]

    def find_type_parser(self, namespace_uri, name):
        """Given namespace_uri and name, find the simple type and create a
        parser function for it that will accept data and convert it into the
        appropriate type."""
        raise NotImplementedError(
            "I don't know how to handle %r %r simple type" % (
                namespace_uri, name))

            



    def parse_filename(self, filename):
        """Parse an XML file identified by filename with this schema."""
        return self.parse(parse_xml_filename(filename))

    def parse_file(self, data_file):
        """Parse an XML file with this schema."""
        return self.parse(parse_xml_file(data_file))

    def parse(self, doc):
        """Parse the entire dom with this schema. This is the principal
        entrance point."""
        return self.parse_global_element(*doc.children)

    def parse_global_element(self, data_element):
        """Find the matching global element and parse the data_element with
        it."""
        return self.parse_element(
            self.find_global_element_by_element(data_element),
            data_element)

    def parse_simple_element(self, schema_element, data_element):
        """Parse a single data_element given the matching schema_element which
        is a simple element."""
        type_parser = self.find_type_parser(*schema_element.translate_name(
            schema_element.attr[u'type']))
        try:
            data, = data_element.children
        except ValueError:
            raise ValueError(
                "Expected %r to only have text as data." % (data_element,))

        return type_parser(data)



    def parse_attr(self, schema_element, data_element):
        """Get the value from data_element.attr given schema_element that is
        an 'attribute'"""

        schema_attr = schema_element.attr
        data_attr = data_element.attr
        name = schema_attr[u'name']
        type_name = schema_attr[u'type']
        use = schema_attr.get(u'use')

        value = data_attr.get(name)

        if value is None:
            if use == u'required':
                raise ValueError("%r should have attribute %s" % (
                    data_element, name))
            return None

        type_namespace_uri, type_name = \
            schema_element.translate_name(type_name)

        return self.parse_data_as_simple_type(
            type_namespace_uri, type_name, value)

    def parse_element_with_complex_type(self, complexType, data_element):
        """Parse a complexType"""

        attrs = {}

        did_body = False
        sequence = None
        simpleContent = None
        for child in complexType.children:
            
            if isinstance(child, unicode) and child.isspace():
                continue

            if child.fullname == (self.xml_schema_uri, 'attribute'):
                name = child.attr[u'name']
                attrs[name] = self.parse_attr(child, data_element)
                continue

            if child.fullname == (self.xml_schema_uri, u'sequence'):
                if did_body:
                    raise ValueError("already did body")

                sequence = self.parse_sequence(child, data_element)
                did_body = True
                continue

            if child.fullname == (self.xml_schema_uri, u'simpleContent'):
                if did_body:
                    raise ValueError("already did body")

                simpleContent = self.parse_simple_content(child, data_element)
                did_body = True
                continue

            raise NotImplementedError(repr(child))

        # Missing body OK
        if simpleContent:
            for key, value in attrs:
                setattr(simpleContent, key, value)
            return simpleContent

        elif sequence:
            attrs.update(sequence)
            return attrs

        return attrs

    def parse_sequence(self, sequence, data_element):

        result = {}

        # Walk through the data and the ct together
        # We need a copy of both child arrays
        sequence_children = sequence.children[:]
        data_children = data_element.children[:]

        # Go through each of the sequence children, finding as many matches as
        # you can.
        seen_names = set()
        while sequence_children:
            # Expect an element described by the first element in
            # sequence_children
            schema_item = sequence_children.pop(0)

            # Skip whitespace
            if isinstance(schema_item, unicode):
                if schema_item.isspace():
                    continue
                else:
                    raise ValueError("Unexpected text: %r" % schema_item)

            if schema_item.fullname != (self.xml_schema_uri, 'element'):
                raise ValueError("Unexpected child: %r" % (schema_item,))

            minOccurs = int(schema_item.attr.get('minOccurs', 1))
            maxOccurs = schema_item.attr.get('maxOccurs', 1)
            if maxOccurs == u'unbounded':
                maxOccurs = None
            else:
                maxOccurs = int(maxOccurs)

            # Deref if ref
            if u'ref' in schema_item.attr:
                ref = schema_item.attr[u'ref']
                schema_item = self.find_global_element_by_name(
                    *schema_item.translate_name(ref))

            expected_name = schema_item.attr[u'name']

            collected = []
            while data_children:
                data_item = data_children[0]
                if data_item.name == expected_name:
                    collected.append(self.parse_element(
                        schema_item,
                        data_children.pop(0)))
                    if len(collected) == maxOccurs:
                        break
                else:
                    break

            if len(collected) < minOccurs:
                raise ValueError(
                    "Element %r occurred only %d times, "
                    "not %d as expected." % (
                        expected_name, len(collected), minOccurs))

            # Don't bother storing empty collections
            if collected:
                result.setdefault(expected_name, [])
                result[expected_name].extend(collected)

        if data_children:
            raise ValueError("Didn't match all the chidren")

        for key, value in result.items():
            if len(value) == 1:
                result[key] = value[0]
                
        return result

    def parse_simple_content(self, simpleContent, data_element):
        """Parse a <simpleContent> inside a <complexType>"""

        child, = [child
            for child in simpleContent.children
            if not isinstance(child, unicode)]

        if child.fullname == (self.xml_schema_uri, u'extension'):
            return self.parse_extension(child, data_element)

        raise NotImplementedError

    def parse_extension(self, extension, data_element):
        """Parse a <extension> in <simpleContent> in <complexType>"""

        # Grab the data
        base = extension.attr['base']

        type_namespace_uri, type_name = extension.translate_name(base)

        value = self.parse_element_by_type(
            type_namespace_uri, type_name, data_element)

        # Create a new class, just for this value, derived from the type of
        # the value and initialized with the value.
        result = type(str(extension.name), (type(value),), {})(value)

        # Grab stuff inside this
        for child in extension.children:
            if isinstance(child, unicode) and child.isspace():
                continue

            if child.fullname == (self.xml_schema_uri, 'attribute'):
                name = child.attr['name']
                setattr(result, name, self.parse_attr(child, data_element))
                continue

            raise NotImplementedError(repr(child))

        return result

    def parse_element_with_simple_type(self, simpleType, data_element):
        """Parse a simpleType"""
        pass

    def parse_element_as_builtin_type(self, type_name, data_element):
        """Parse an element as a simple type."""

        if not data_element.only_text():
            raise ValueError(
                "Expected %r to only have text" % (data_element,))

        return self.parse_data_as_builtin_type(
            type_name, data_element.children[0])

    def parse_data_as_simple_type(self, type_namespace_uri, type_name, data):
        """Find the builtin or simple type represented by type_name and parse
        data with it."""
        if type_namespace_uri == self.xml_schema_uri:
            return self.parse_data_as_builtin_type(type_name, data)

        raise NotImplementedError()

    def parse_data_as_builtin_type(self, type_name, data):
        if type_name == 'QName':
            # I'd need to see what element is the context for this to work.
            raise NotImplementedError

        return self.builtin_simple_types[type_name](data)


    def parse_element_by_type(self,
            type_namespace_uri, type_name, data_element):
        """Given a type element (simpleType or complexType), parse the
        data_element and return a value representing it."""

        # Lookup the type.
        if type_namespace_uri == self.xml_schema_uri:
            return self.parse_element_as_builtin_type(type_name, data_element)

        try:
            complexType = self.complexTypes[type_namespace_uri, type_name]
        except KeyError:
            pass
        else:
            return self.parse_element_with_complex_type(complexType, data_element)
            
        try:
            simpleType = self.simpleTypes[type_namespace_uri, type_name]
        except KeyError:
            pass
        else:
            return self.parse_element_with_simple_type(simpleType, data_element)

        raise NotImplementedError("%r" % ((type_namespace_uri, type_name),))


    def parse_element(self, schema_element, data_element):
        """Parse a single data_element given the matching schema_element"""
        # Expect the schema_element to have sequence inside complexType.
        #print "parse_element(%r, %r)" % (schema_element, data_element)

        # TODO: When I lookup the type, it can be one of three things:
        #   * A built-in type, such as "xs:string"
        #   * A simpleType
        #   * A complexType
        #   I need to branch based on what it is and behave differently each
        #   time.
        #
        #   If there is no type, then I need to look to see what kind of type
        #   it is by looking at the first (and hopefully only) child. Based on
        #   that, I need to branch.

        type_ = schema_element.attr.get(u'type')
        if type_ is not None:
            type_namespace_uri, type_name = \
                schema_element.translate_name(type_)

            return self.parse_element_by_type(
                type_namespace_uri, type_name, data_element)

        child, = [child
            for child in schema_element.children
            if not isinstance(child, unicode)]

        if child.fullname == (self.xml_schema_uri, u'complexType'):
            return self.parse_element_with_complex_type(
                child, data_element)

        if child.fullname == (self.xml_schema_uri, u'simpleType'):
            return self.parse_element_with_simple_type(
                child, data_element)

        raise NotImplementedError



