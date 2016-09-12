from zeit.cms.tagging.interfaces import ID_NAMESPACE as TAG_NAMESPACE
import json
import zeit.cms.interfaces
import zeit.cms.tagging.browser.widget
import zeit.cms.tagging.tag


class IntrafindTagWidget(zeit.cms.tagging.browser.widget.Widget):
    """Edit widget for tags from intrafind.

    We need this here to work around an edge case, when the intrafind
    ``Tagger`` adds tags, which are not in the ``Whitelist``.

    """

    def _toFieldValue(self, value):
        tags = json.loads(value)
        result = []
        for item in tags:
            try:
                tag = zeit.cms.interfaces.ICMSContent(item['code'])
            except TypeError:
                # XXX stopgap until we find out about #12609
                tag = zeit.cms.tagging.tag.Tag(
                    item['code'].replace(TAG_NAMESPACE, ''), item['label'])
            tag.pinned = item['pinned']
            result.append(tag)
        return tuple(result)
