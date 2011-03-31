# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import logging
import lxml.objectify
import urllib
import urllib2
import zeit.cms.content.dav
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.intrafind.interfaces
import zope.app.appsetup.product
import zope.interface


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging/"
log = logging.getLogger(__name__)


class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.cms.tagging.interfaces.ITagger)

    def __iter__(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        prefix_len = len(NAMESPACE)
        # The world has seen more efficient code.
        ids = set(namespace[prefix_len:] for (name, namespace) in dav
                  if namespace.startswith(NAMESPACE))
        tags = (self.get(code) for code in ids)
        sorted_tags = sorted((tag for tag in tags if tag is not None),
                             key=lambda tag: tag.weight,
                             reverse=True)
        return (tag.code for tag in sorted_tags)

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        tag = zope.component.queryMultiAdapter(
            (self.context, key), zeit.intrafind.interfaces.ITag)
        if tag is None:
            raise KeyError(key)
        # XXX tag doesn't provide ILocation, yet
        tag.__name__ = key
        tag.__parent__ = self
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
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        return ('label', NAMESPACE + key) in dav

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


class TagProperty(object):

    def __init__(self, key):
        self.key = key

    def __get__(self, instance, class_):
        prop = self._get_property(instance, self.key)
        return prop.__get__(instance, class_)

    def __set__(self, instance, value):
        prop = self._get_property(instance, self.key)
        return prop.__set__(instance, value)

    def _get_property(self, instance, key):
        return zeit.cms.content.dav.DAVProperty(
            zeit.intrafind.interfaces.ITag[key],
            NAMESPACE + instance.code, key)


class Tag(object):

    zope.interface.implements(zeit.intrafind.interfaces.ITag)

    for _attr in ('label', 'status', 'frequency', 'score', 'disabled',
                  'type', 'weight'):
        locals()[_attr] = TagProperty(_attr)
    del _attr

    def __init__(self, context, code):
        self.context = context
        self.code = code

    def __eq__(self, other):
        if zeit.cms.tagging.interfaces.ITag.providedBy(other):
            return other.code == self.code
        return NotImplemented

    def __hash__(self):
        return hash(self.code)


@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent, basestring)
@grokcore.component.implementer(zeit.intrafind.interfaces.ITag)
def existing_tag_factory(context, code):
    tag = Tag(context, code)
    if not tag.label:
        return None
    return tag


@grokcore.component.adapter(Tag)
@grokcore.component.implementer(zeit.connector.interfaces.IWebDAVProperties)
def tag_webdavproperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)
