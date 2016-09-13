import zeit.intrafind.testing
import zeit.cms.interfaces
import zeit.cms.testing
import zope.component


class TestTag(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.intrafind.testing.ZCML_LAYER

    def test_uniqueId_from_tag_can_be_adapted_to_tag(self):
        from zeit.intrafind.tag import Tag
        tag = Tag('uid-foo', 'Foo')
        wl = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        wl.data['uid-foo'] = tag
        self.assertEqual(tag, zeit.cms.interfaces.ICMSContent(tag.uniqueId))
