# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import logging
import lxml.objectify
import urllib
import urllib2
import xml.sax.saxutils
import zeit.cms.content.dav
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.interface


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging"
KEYWORD_PROPERTY = ('rankedTags', NAMESPACE)
DISABLED_PROPERTY = ('disabled', NAMESPACE)
DISABLED_SEPARATOR = '\x09'

log = logging.getLogger(__name__)


class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.cms.tagging.interfaces.ITagger)

    def __iter__(self):
        tags = self._parse()
        if tags is None:
            return iter(())
        return (x.get('uuid') for x in tags.iterchildren())

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        node = self._find_tag_node(key)
        tag = zeit.cms.tagging.tag.Tag(node.get('uuid'), unicode(node))
        tag.__parent__ = self
        tag.__name__ = tag.code
        return tag

    def values(self):
        return (self[code] for code in self)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        raise NotImplementedError()

    def items(self):
        raise NotImplementedError()

    def __contains__(self, key):
        return key in list(self)

    def updateOrder(self, keys):
        if set(keys) != set(self):
            raise ValueError(
                'Must pass in the same keys already present %r, not %r'
                % (list(self), keys))
        orderd = []
        tags = self._parse()
        for key in keys:
            tag = self._find_tag_node(key, tags)
            orderd.append(tag)
            tags.remove(tag)
        tags.extend(orderd)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(tags.getroottree())

    def __delitem__(self, key):
        node = self._find_tag_node(key)
        node.getparent().remove(node)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(node.getroottree())

        disabled = dav.get(DISABLED_PROPERTY)
        if disabled is None:
            disabled = []
        else:
            disabled = disabled.split(DISABLED_SEPARATOR)
        disabled.append(key)
        dav[DISABLED_PROPERTY] = DISABLED_SEPARATOR.join(disabled)

    def _parse(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        try:
            tags = lxml.objectify.fromstring(dav.get(KEYWORD_PROPERTY, ''))
        except lxml.etree.XMLSyntaxError:
            return None
        if tags.tag != '{{{1}}}{0}'.format(*KEYWORD_PROPERTY):
            return None
        return tags.getchildren()[0]

    def _find_tag_node(self, key, tags=None):
        if tags is None:
            tags = self._parse()
        if tags is None:
            raise KeyError(key)
        node = tags.xpath('//tag[@uuid = {0}]'.format(
                xml.sax.saxutils.quoteattr(key)))
        if not node:
            raise KeyError(key)
        return node[0]

    # XXX the update methods need to be rewritten for #9827

    def update(self):
        log.info('Updating tags for %s', self.context.uniqueId)
        body = zeit.connector.interfaces.IResource(self.context).data.read()
        data = urllib.urlencode(dict(content=body))
        response = urllib2.urlopen(self._intrafind_url, data, 10)
        xml = lxml.objectify.parse(response)
        self._clear()
        self._load_from(xml)

    def _clear(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        for code in list(self):
            remove_namespace = NAMESPACE + code
            for name, namespace in list(dav.keys()):
                if namespace == remove_namespace and name != 'disabled':
                    del dav[(name, namespace)]

    def _load_from(self, xml):
        for tag_xml in xml.findall('//tag'):
            code = tag_xml.get('id')
            tag = Tag(self.context, code)
            label = unicode(tag_xml).strip()
            tag.label = label
            assert label == tag.label
            tag.frequency = tag_xml.get('freq')
            tag.score = tag_xml.get('score')
            tag.status = tag_xml.get('status')
            tag.type = tag_xml.get('type')

    @property
    def _intrafind_url(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.intrafind')
        return config['tagger']
