__ALL__ = [
    'parse_xml_filename',
    'parse_xml_file'
]

from Element import Element
from Document import Document
from xml.parsers import expat

def parse_xml_filename(filename):
    return parse_xml_file(file(filename, "r"))

def parse_xml_file(file_):
    stack = []

    def xml_decl_handler(version, encoding, standalone):
        if stack:
            raise ValueError("didn't expect it to end so soon")
        stack.append(Document(version, standalone))

    def default_handler(data):
        if isinstance(data, unicode) and data.isspace():
            pass
        else:
            raise ValueError("Didn't expect %r" % (data,))

    def start_handler(name, attributes):
        el = Element(name, attributes, stack[-1].namespace)
        stack[-1].children.append(el)
        stack.append(el)

    def end_handler(name):
        stack.pop(-1)

    def data_handler(data):
        top_children = stack[-1].children
        if top_children and isinstance(top_children[-1], unicode):
            top_children[-1] += data
        else:
            top_children.append(data)

    parser = expat.ParserCreate()
    parser.XmlDeclHandler = xml_decl_handler
    parser.DefaultHandlerExpand = default_handler
    parser.StartElementHandler = start_handler
    parser.EndElementHandler = end_handler
    parser.CharacterDataHandler = data_handler

    parser.ParseFile(file_)

    if len(stack) != 1:
        raise ValueError("Stack is wrong")

    return stack[0]
