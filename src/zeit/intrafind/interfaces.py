# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


class ITag(zope.interface.Interface):
    """A generic tag on an object."""

    id = zope.schema.TextLine(
        title=_('Internal tag id'))

    text = zope.schema.TextLine(
        title=_('User visible text of tag'))

    status = zope.schema.Choice(
        title=_('Tag status'),
        description=_(
            'tag-status-description',
            default=(u'Known tags are on the whitelist.  New tags need to be '
                     u'whitelisted to be visible in public.')),
        values=('known', 'new'))

    type = zope.interface.Attribute(
        "Tag type (person, topic, keyword, ...)")


    frequency = zope.schema.Int(
        title=_('Tag frequency in document'),
        minvalue=1)

    score = zope.schema.Float(
        title=_('Tag score for document'),
        minvalue=0,
        maxvalue=1)
