# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2
import zeit.cms.testing


class TestTagger(zeit.cms.testing.FunctionalTestCase,
                 unittest2.TestCase):

    def get_content(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        return TestContentType()

    def get_tagger(self, content):
        from zeit.intrafind.tagger import Tagger
        return Tagger(content)

    def set_tag(self, content, id, **kw):
        from zeit.connector.interfaces import IWebDAVProperties
        dav = IWebDAVProperties(content)
        for key, value in kw.items():
            dav_key = (
                key, 'http://namespaces.zeit.de/CMS/tagging/{0}'.format(id))
            dav[dav_key] = value

    def test_should_adapt_contetXXX(self):
        pass

    def test_update_should_post_xml_to_intrafind(self):
        pass

    def test_update_should_extract_tags_from_response(self):
        pass

    def test_update_should_change_content(self):
        pass

    def test_tagger_should_be_empty_if_not_tagged(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertEqual([], list(tagger))

    def test_tagger_should_init_tags_from_content(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', text='Karen Duve')
        self.set_tag(content, id='Berlin', text='Berlin')
        tagger = self.get_tagger(content)
        self.assertEqual(set(['Berlin', 'Karen+Duve']), set(tagger))

    def test_len_should_return_amount_of_tags(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', text='Karen Duve')
        self.set_tag(content, id='Berlin', text='Berlin')
        tagger = self.get_tagger(content)
        self.assertEqual(2, len(tagger))
        self.set_tag(content, id='Fleisch', text='Fleisch')
        self.assertEqual(3, len(tagger))

    def test_tags_should_be_accessible_by_id(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', text='Karen Duve')
        self.set_tag(content, id='Berlin', text='Berlin')
        tagger = self.get_tagger(content)
        tag = tagger['Karen+Duve']
        self.assertEqual(tagger, tag.__parent__)
        self.assertEqual('Karen+Duve', tag.__name__)
        self.assertEqual('Karen Duve', tag.text)

