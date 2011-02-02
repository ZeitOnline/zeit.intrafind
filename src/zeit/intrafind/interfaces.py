# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema
import zeit.cms.tagging.interfaces


class ITag(zeit.cms.tagging.interfaces.ITag):
    """A generic tag on an object."""

    status = zope.schema.Choice(
        title=_('Tag status'),
        description=_(
            'tag-status-description',
            default=(u'Known tags are on the whitelist.  New tags need to be '
                     u'whitelisted to be visible in public.')),
        values=('known', 'new'))

    frequency = zope.schema.Int(
        title=_('Tag frequency in document'),
        min=1,
        required=False)

    score = zope.schema.Float(
        title=_('Tag score for document'),
        min=0.0,
        max=1.0,
        required=False)
