__ALL__ = [
    'Element'
]

class Element(object):
    """An XML element specific for our needs.

name: The tag name, without namespace qualifiers.

namespace_uri: The URL of the namespace.

fullname: (read only) (namespace_uri, name)

children: The children. This will include a mix of unicode and Elements.
          Unicode represents text.

attr: The attribute dictionary. This includes 'xmlns:' declarators.

namespace: The namespace of this element. This is likely a copy of the parent
           node, but may be modified if there are "xmlns:" attributes. Note
           that el.namespace[el.namespace_id] == el.namespace_uri.
"""

    def __init__(self, name, attr, parent_namespace):
        self.children = []
        self.attr = attr
        
        # Calculate our namespace
        new_namespace = dict()
        for attr_name, attr_value in attr.items():
            if attr_name == u'xmlns':
                new_namespace[u''] = attr_value
            elif attr_name[:6] == u'xmlns:':
                new_namespace[attr_name[6:]] = attr_value

        if not new_namespace:
            self.namespace = parent_namespace
        else:
            namespace = parent_namespace.copy()
            namespace.update(new_namespace)
            new_namespace = namespace
            self.namespace = new_namespace

        self.namespace_uri, self.name = self.translate_name(name)

    def translate_name(self, name):
        """Given 'namespace_id:name', or even just 'name', translate it into a
        (namespace_url, name) pair."""
        if name.find(':') >= 0:
            namespace_id, name = name.split(':', 1)
        else:
            namespace_id = u''
        namespace_uri = self.namespace[namespace_id]
        return namespace_uri, name

    def get_fullname(self):
        return self.namespace_uri, self.name
    fullname = property(get_fullname)

    def findall(self, namespace_uri, name):
        for child in self.children:
            if isinstance(child, unicode):
                continue
            if child.namespace_uri == namespace_uri \
                    and child.name == name:
                yield child

    def only_text(self):
        return len(self.children) == 1 \
            and isinstance(self.children[0], unicode)

    def __repr__(self):
        attrs = " ".join(['%s="%s"' % (key, value) \
            for key, value in self.attr.items()])

        if attrs: attrs += ' '

        return '<%s xmlns="%s" %sat %#x>' % (
            self.name, self.namespace_uri, attrs, id(self))
