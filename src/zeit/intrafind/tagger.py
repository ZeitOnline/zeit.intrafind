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
        ids = (namespace[prefix_len:] for (name, namespace) in dav
               if namespace.startswith(NAMESPACE) and name == 'label')
        return ids

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        tag = zope.component.queryMultiAdapter(
            (self.context, key), zeit.intrafind.interfaces.ITag)
        if tag is None:
            raise NotImplementedError('no test for this, yet')
            raise KeyError(key)
        tag.__name__ = key
        tag.__parent__ = self
        return tag

    def values(self):
        return (self[code] for code in self)


class Tag(grokcore.component.MultiAdapter):

    grokcore.component.implements(zeit.intrafind.interfaces.ITag)
    grokcore.component.adapts(zeit.cms.interfaces.ICMSContent, basestring)

    def __new__(cls, context, code):
        dav = zeit.connector.interfaces.IWebDAVProperties(context)
        # To be able to use exsting descriptors we factor a new class on the
        # fly. There may be more elegant ways to do this.
        instance_dict = {}
        for key in ('label', 'status', 'frequency', 'score', 'active', 'type'):
            instance_dict[key] = zeit.cms.content.dav.DAVProperty(
                zeit.intrafind.interfaces.ITag[key], NAMESPACE + code, key)
        tag_class = type('Tag({0})'.format(code), (Tag,), instance_dict)
        tag = object.__new__(tag_class)
        tag.context = context
        tag.code = code
        if not tag.label:
            return None
        return tag

    def __eq__(self, other):
        if zope.security.proxy.isinstance(other, Tag):
            return other.code == self.code
        return NotImplemented


    def __unicode__(self):
        return self.label



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

