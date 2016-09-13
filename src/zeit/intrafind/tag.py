import zope.interface
import zeit.cms.tagging.interfaces
import zeit.cms.interfaces


class Tag(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, code, label, pinned=False, entity_type=None,
                 url_value=None):
        self.code = code
        self.label = label
        self.pinned = pinned
        self.entity_type = entity_type
        self.url_value = url_value

    def __eq__(self, other):
        # XXX this is not a generic equality check. From a domain perspective,
        # two tags are the same when their codes are the same. However, since
        # we want to edit ``pinned``, and formlib compares the *list* of
        # keywords, which uses == on the items, we need to include pinned here.
        if other is None:
            return False
        return self.code == other.code and self.pinned == other.pinned

    @property
    def uniqueId(self):
        return zeit.cms.tagging.interfaces.ID_NAMESPACE + self.code
