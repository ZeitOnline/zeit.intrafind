# coding: utf-8
# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import unittest2 as unittest
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

    layer = zeit.intrafind.testing.layer

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

    def test_getitem_should_raise_keyerror_if_tag_does_not_exist(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertRaises(KeyError, lambda: tagger['foo'])

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


class TaggerUpdateTest(zeit.cms.testing.FunctionalTestCase, TagTestHelpers):

    layer = zeit.intrafind.testing.layer

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
