# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.connector.interfaces

NAMESPACE = "http://namespaces.zeit.de/CMS/tagging/"

class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):

    def __iter__(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        prefix_len = len(NAMESPACE)
        ids = (namespace[prefix_len:] for (name, namespace) in dav
               if namespace.startswith(NAMESPACE) and name == 'text')
        return ids

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        text = dav[('text', NAMESPACE + key)]
        tag = Tag(text)
        tag.__name__ = key
        tag.__parent__ = self
        return tag


class Tag(object):

    def __init__(self, text):
        self.text = text

