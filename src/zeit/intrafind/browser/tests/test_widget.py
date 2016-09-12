from __future__ import unicode_literals
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.intrafind.testing
import zope.publisher.browser


class InputWidget(zeit.cms.testing.FunctionalTestCase):
    """tests ..widget.IntrafindTagWidget"""

    layer = zeit.intrafind.testing.ZCML_LAYER

    def test_returns_tag_that_is_not_in_whitelist(self):
        from zeit.intrafind.browser.widget import IntrafindTagWidget
        request = zope.publisher.browser.TestRequest(
            form={'field.keywords': (
                '[{"code": "tag://t1", "label": "t1", "pinned": true}]')})

        widget = IntrafindTagWidget(
            zeit.cms.content.interfaces.ICommonMetadata['keywords'],
            None, request)
        tags = widget._toFieldValue(widget._getFormInput())
        self.assertEqual(1, len(tags))
