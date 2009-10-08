#!/usr/bin/env python
"""Contains a special version of an XML Document."""

__ALL__ = [
    'Document'
]

class Document(object):
    """A special version of an XML Document specific for the XMLSchemaParser.

version: The XML version.

standalone: Whether the document is standalone.

children: The child elements. (This is a list to make it compliant with an
          Element.)

namespace: The namespace of the document.
"""

    def __init__(self, version, standalone):
        self.version = version
        self.standalone = standalone
        self.children = []
        self.namespace = {}
