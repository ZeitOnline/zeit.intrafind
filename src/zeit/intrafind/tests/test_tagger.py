# coding: utf-8
# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import zeit.cms.testing
import zeit.intrafind.testing


class TagTestHelpers(object):

    def get_content(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        return TestContentType()

    def set_tags(self, content, xml):
        from zeit.connector.interfaces import IWebDAVProperties
        dav = IWebDAVProperties(content)
        name, ns = dav_key = (
            'rankedTags', 'http://namespaces.zeit.de/CMS/tagging')
        dav[dav_key] = """<ns:{tag} xmlns:ns="{ns}">
        <rankedTags>{0}</rankedTags></ns:{tag}>""".format(
            xml, ns=ns, tag=name)

    def get_tagger(self, content):
        from zeit.intrafind.tagger import Tagger
        return Tagger(content)


class TestTagger(zeit.cms.testing.FunctionalTestCase, TagTestHelpers):

    layer = zeit.intrafind.testing.ZCML_LAYER

    def test_tagger_should_provide_interface(self):
        import zope.interface.verify
        from zeit.cms.tagging.interfaces import ITagger
        self.assertTrue(
            zope.interface.verify.verifyObject(
                ITagger, self.get_tagger(self.get_content())))

    def test_tagger_should_be_empty_if_not_tagged(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertEqual([], list(tagger))

    def test_tagger_should_get_tags_from_content(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual(set(['uid-berlin', 'uid-karenduve']), set(tagger))

    def test_len_should_return_amount_of_tags(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual(2, len(tagger))
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        self.assertEqual(3, len(tagger))

    def test_tags_should_be_accessible_by_id(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        tag = tagger['uid-karenduve']
        self.assertEqual(tagger, tag.__parent__)
        self.assertEqual('uid-karenduve', tag.__name__)
        self.assertEqual('Karen Duve', tag.label)

    def test_tag_should_have_entity_type(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin" type="Location">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual('Location', tagger['uid-berlin'].entity_type)

    def test_tag_should_have_url_value(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin" url_value="dickesb">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual('dickesb', tagger['uid-berlin'].url_value)

    def test_getitem_should_raise_keyerror_if_tag_does_not_exist(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertRaises(KeyError, lambda: tagger['foo'])

    def test_setitem_should_add_tag(self):
        from zeit.cms.tagging.tag import Tag
        content = self.get_content()
        tagger = self.get_tagger(content)
        tagger['uid-berlin'] = Tag('uid-berlin', 'Berlin')
        self.assertEqual(['uid-berlin'], list(tagger))
        self.assertEqual('Berlin', tagger['uid-berlin'].label)

    def test_setitem_should_set_entity_type(self):
        from zeit.cms.tagging.tag import Tag
        content = self.get_content()
        tagger = self.get_tagger(content)
        tagger['uid-berlin'] = Tag(
            'uid-berlin', 'Berlin', entity_type='Location')
        self.assertEqual('Location', tagger['uid-berlin'].entity_type)

    def test_iter_should_be_sorted_by_document_order(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual(
            ['uid-berlin', 'uid-karenduve', 'uid-fleisch'], list(tagger))

    def test_updateOrder_should_sort_tags(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = self.get_tagger(content)
        tagger.updateOrder(['uid-fleisch', 'uid-berlin', 'uid-karenduve'])
        self.assertEqual(
            ['uid-fleisch', 'uid-berlin', 'uid-karenduve'], list(tagger))

    def test_updateOrder_should_sort_tags_even_when_keys_are_generator(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = self.get_tagger(content)
        tagger.updateOrder(
            iter(['uid-fleisch', 'uid-berlin', 'uid-karenduve']))
        self.assertEqual(
            ['uid-fleisch', 'uid-berlin', 'uid-karenduve'], list(tagger))

    def test_given_keys_differ_from_existing_keys_should_raise(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = self.get_tagger(content)
        self.assertRaises(
            ValueError,
            lambda: tagger.updateOrder(['uid-berlin', 'uid-karenduve']))

    def test_contains_should_return_true_for_existing_tag(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = self.get_tagger(content)
        self.assertIn('uid-karenduve', tagger)

    def test_contains_should_return_false_for_noneexisting_tag(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertNotIn('uid-karenduve', tagger)

    def test_get_should_return_existing_tag(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = self.get_tagger(content)
        self.assertEqual('Karen Duve', tagger.get('uid-karenduve').label)

    def test_get_should_return_default_if_tag_does_not_exist(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertEqual(mock.sentinel.default,
                         tagger.get('uid-karenduve', mock.sentinel.default))

    def test_delitem_should_remove_tag(self):
        content = self.get_content()
        # use an umlaut to exercise serialization
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Düve</tag>
""")
        tagger = self.get_tagger(content)
        del tagger['uid-karenduve']
        self.assertNotIn('uid-karenduve', tagger)

    def test_delitem_should_add_tag_to_disabled_list_in_dav(self):
        from zeit.connector.interfaces import IWebDAVProperties

        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = self.get_tagger(content)
        del tagger['uid-karenduve']

        dav = IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-karenduve', dav[dav_key])

    def test_disabled_tags_should_be_separated_by_tab(self):
        from zeit.connector.interfaces import IWebDAVProperties

        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        del tagger['uid-karenduve']

        dav = IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-karenduve', dav[dav_key])

    def test_parse_should_return_inner_rankedTags(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        node = tagger._parse()
        self.assertEqual('rankedTags', node.tag)

    def test_rankedKeys_dav_property_should_not_be_added_to_xml(self):
        import zeit.cms.content.interfaces
        import zope.interface
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        zope.interface.alsoProvides(
            content, zeit.cms.content.interfaces.IDAVPropertiesInXML)
        sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
        sync.sync()
        dav_attribs = u'\n'.join(
            unicode(a) for a in content.xml.head.attribute[:])
        self.assertNotIn('rankedTags', dav_attribs)

    def test_existing_tags_should_cause_rankedTags_to_be_added_to_xml(self):
        import zope.component
        import zeit.cms.repository.interfaces
        import zeit.cms.checkout.helper
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = self.get_content()
        with zeit.cms.checkout.helper.checked_out(repository['content']) as \
                content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
        self.assertEqual(
            ['Karen Duve', 'Berlin'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_no_tags_cause_rankedTags_element_to_be_removed_from_xml(self):
        import zope.component
        import zeit.cms.repository.interfaces
        import zeit.cms.checkout.helper
        content = self.get_content()
        content.xml.head.rankedTags = 'bla bla bla'
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = content
        with zeit.cms.checkout.helper.checked_out(repository['content']):
            # cycle
            pass
        self.assertNotIn('rankedTags', repository['content'].xml.head.keys())

    def test_checkin_should_not_fail_with_no_tags_and_no_rankedTags_element(
        self):
        import zope.component
        import zeit.cms.repository.interfaces
        import zeit.cms.checkout.helper
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = self.get_content()
        with zeit.cms.checkout.helper.checked_out(repository['content']):
            # cycle
            pass

    def test_disabled_tags_should_be_removed_from_xml(self):
        import zope.component
        import zeit.cms.repository.interfaces
        import zeit.cms.checkout.helper
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = self.get_content()
        with zeit.cms.checkout.helper.checked_out(repository['content']) as \
                content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
            tagger = self.get_tagger(content)
            del tagger['uid-berlin']
        self.assertEqual(
            ['Karen Duve'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_rankedTags_in_xml_should_be_updated_on_modified_event(self):
        import zeit.cms.checkout.helper
        import zeit.cms.repository.interfaces
        import zope.component
        import zope.lifecycleevent
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = self.get_content()
        with zeit.cms.checkout.helper.checked_out(repository['content']) as \
                content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
            zope.lifecycleevent.modified(content)
            self.assertEqual(
                ['Karen Duve', 'Berlin'],
                content.xml.head.rankedTags.getchildren())

    def test_modified_event_should_leave_non_content_alone(self):
        # regression #12394
        import zeit.cms.content.interfaces
        import zope.interface
        import zope.lifecycleevent

        dummy = type('Dummy', (object,), {})
        zope.interface.alsoProvides(
            dummy, zeit.cms.content.interfaces.IXMLRepresentation)
        with mock.patch(
                'zeit.intrafind.tagger.add_ranked_tags_to_head') as handler:
            zope.lifecycleevent.modified(dummy)
            self.assertFalse(handler.called)

    def test_set_pinned_should_update_tab_separated_property(self):
        from zeit.connector.interfaces import IWebDAVProperties
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = self.get_tagger(content)
        tagger.set_pinned(['uid-berlin', 'uid-karenduve'])
        self.assertEqual(('uid-berlin', 'uid-karenduve'), tagger.pinned)

        dav = IWebDAVProperties(content)
        dav_key = ('pinned', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-berlin\tuid-karenduve', dav[dav_key])

        self.assertTrue(tagger['uid-berlin'].pinned)


class TaggerUpdateTest(zeit.cms.testing.FunctionalTestCase, TagTestHelpers):

    layer = zeit.intrafind.testing.ZCML_LAYER

    def test_update_should_post_xml_urlencoded_to_intrafind(self):
        handler = zeit.intrafind.testing.RequestHandler
        content = self.get_content()
        tagger = self.get_tagger(content)
        tagger.update()
        self.assertEqual(1, len(handler.posts_received))
        self.assertTrue(handler.posts_received[0]['data'].startswith(
            'xml=%3C%3Fxml+version'))

    def test_update_should_extract_tags_from_response(self):
        handler = zeit.intrafind.testing.RequestHandler
        handler.response_body = pkg_resources.resource_string(
            __name__, 'tagger_response.xml')
        content = self.get_content()
        tagger = self.get_tagger(content)
        tagger.update()
        self.assertEqual(6, len(tagger))

    def test_update_should_clear_disabled_tags(self):
        from zeit.connector.interfaces import IWebDAVProperties
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = self.get_tagger(content)
        del tagger['uid-karenduve']
        tagger.update()
        dav = IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('', dav[dav_key])

    def test_update_should_keep_pinned_tags(self):
        content = self.get_content()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = self.get_tagger(content)
        tagger.set_pinned(['uid-karenduve'])
        tagger.update()
        self.assertEqual(['uid-karenduve'], list(tagger))

    def test_update_should_not_duplicate_pinned_tags(self):
        # this is a rather tricky edge case:
        # when we pin a manual tag first, and then also pin a tag that
        # comes in via update() again, we used to screw it up,
        # since we compared against a generator multiple times
        from zeit.cms.tagging.tag import Tag
        handler = zeit.intrafind.testing.RequestHandler
        handler.response_body = pkg_resources.resource_string(
            __name__, 'tagger_response.xml')
        content = self.get_content()
        tagger = self.get_tagger(content)
        tagger.update()
        self.assertEqual(6, len(tagger))
        tagger['uid-karenduve'] = Tag('uid-karenduve', 'Karen Duve')
        tagger.set_pinned([
            'uid-karenduve', 'aa23f170-65a2-4a00-8fec-006a3b4b73d2'])
        tagger.update()
        self.assertEqual(
            [u'Feiertag', u'USA', u'Post',
             u'Verlag', u'New York', u'Reims', u'Karen Duve'],
            [tagger[x].label.strip() for x in tagger])
