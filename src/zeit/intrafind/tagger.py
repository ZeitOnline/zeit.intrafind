# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import logging
import lxml.objectify
import urllib
import urllib2
import xml.sax.saxutils
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.interface
import zope.lifecycleevent
import zope.security.proxy


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
        keys = list(keys)  # in case we've got a generator
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

    def update(self):
        log.info('Updating tags for %s', self.context.uniqueId)
        body = zeit.connector.interfaces.IResource(self.context).data.read()
        data = urllib.urlencode(dict(xml=body))
        response = urllib2.urlopen(self._intrafind_url, data, 10)
        __traceback_info__ = (response.code,)
        xml = lxml.objectify.fromstring(response.read())
        self._load_from(xml)

    def _load_from(self, xml):
        root = lxml.objectify.ElementMaker(namespace=NAMESPACE).rankedTags()
        tags = xml.find('rankedTags')
        if tags is not None:
            root.append(xml['rankedTags'])
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(root.getroottree())
        dav[DISABLED_PROPERTY] = u''

    @property
    def _intrafind_url(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.intrafind')
        return config['tagger']


@grokcore.component.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def veto_tagging_properties(event):
    if event.namespace == NAMESPACE:
        event.veto()


def add_ranked_tags_to_head(content):
    tagger = zeit.cms.tagging.interfaces.ITagger(content, None)
    xml = zope.security.proxy.removeSecurityProxy(content.xml)
    if tagger:
        xml.head.rankedTags = zope.security.proxy.removeSecurityProxy(
                tagger)._parse()
    else:
        try:
            del xml.head.rankedTags
        except AttributeError:
            pass


@grokcore.component.subscribe(
    zeit.cms.content.interfaces.IXMLRepresentation,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_tags_on_checkin(content, event):
    # ICMSContent.providedBy(content) is True implicitly, since otherwise one
    # wouldn't be able to check it in.
    add_ranked_tags_to_head(content)


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.ObjectModifiedEvent)
def update_tags_on_modify(content, event):
    if not zeit.cms.content.interfaces.IXMLRepresentation.providedBy(content):
        return
    add_ranked_tags_to_head(content)
