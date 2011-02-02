# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zc.sourcefactory.interfaces
import zeit.cms.content.dav
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.intrafind.interfaces
import zope.interface
import zope.security.proxy


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging/"


class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.cms.tagging.interfaces.ITagger)

    def __iter__(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        prefix_len = len(NAMESPACE)
        # The world has seen more efficient code.
        ids = set(namespace[prefix_len:] for (name, namespace) in dav
                  if namespace.startswith(NAMESPACE))
        sorted_tags = sorted((self[code] for code in ids),
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



class Tag(grokcore.component.MultiAdapter):

    grokcore.component.implements(zeit.intrafind.interfaces.ITag)
    grokcore.component.adapts(zeit.cms.interfaces.ICMSContent, basestring)

    for _attr in ('label', 'status', 'frequency', 'score', 'disabled',
                  'type', 'weight'):
        locals()[_attr] = TagProperty(_attr)
    del _attr

    def __new__(cls, context, code):
        tag = object.__new__(cls)
        tag.context = context

        tag.code = code
        if not tag.label:
            return None
        return tag

    def __eq__(self, other):
        if zope.security.proxy.isinstance(other, Tag):
            return other.code == self.code
        return NotImplemented

    def __hash__(self):
        return hash(self.code)


@grokcore.component.adapter(Tag)
@grokcore.component.implementer(zeit.connector.interfaces.IWebDAVProperties)
def tag_webdavproperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)



@grokcore.component.adapter(Tag)
@grokcore.component.implementer(zc.sourcefactory.interfaces.IToken)
def token_for_tag(tag):
    return tag.__name__



# TODO:
# saving of selected/deselected tags

