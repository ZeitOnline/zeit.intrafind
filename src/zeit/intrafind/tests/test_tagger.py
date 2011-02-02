# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2
import zeit.cms.testing
import zeit.intrafind.testing


class TagTestHelpers(object):

    def get_content(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        return TestContentType()

    def set_tag(self, content, id, **kw):
        from zeit.connector.interfaces import IWebDAVProperties
        dav = IWebDAVProperties(content)
        for key, value in kw.items():
            dav_key = (
                key, 'http://namespaces.zeit.de/CMS/tagging/{0}'.format(id))
            dav[dav_key] = value


class TestTagger(zeit.cms.testing.FunctionalTestCase,
                 unittest2.TestCase,
                 TagTestHelpers):

    layer = zeit.intrafind.testing.layer

    def get_tagger(self, content):
        from zeit.intrafind.tagger import Tagger
        return Tagger(content)

    def test_tagger_should_provide_interface(self):
        import zope.interface.verify
        from zeit.cms.tagging.interfaces import ITagger
        self.assertTrue(
            zope.interface.verify.verifyObject(
                ITagger, self.get_tagger(self.get_content())))

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
        self.set_tag(content, id='Karen+Duve', label='Karen Duve')
        self.set_tag(content, id='Berlin', label='Berlin')
        tagger = self.get_tagger(content)
        self.assertEqual(set(['Berlin', 'Karen+Duve']), set(tagger))

    def test_len_should_return_amount_of_tags(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', label='Karen Duve')
        self.set_tag(content, id='Berlin', label='Berlin')
        tagger = self.get_tagger(content)
        self.assertEqual(2, len(tagger))
        self.set_tag(content, id='Fleisch', label='Fleisch')
        self.assertEqual(3, len(tagger))

    def test_tags_should_be_accessible_by_id(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', label='Karen Duve')
        self.set_tag(content, id='Berlin', label='Berlin')
        tagger = self.get_tagger(content)
        tag = tagger['Karen+Duve']
        self.assertEqual(tagger, tag.__parent__)
        self.assertEqual('Karen+Duve', tag.__name__)
        self.assertEqual('Karen Duve', tag.label)

    def test_getitem_should_raise_keyerror_if_tag_does_not_exist(self):
        content = self.get_content()
        tagger = self.get_tagger(content)
        self.assertRaises(KeyError, lambda: tagger['foo'])


    def test_remove_should_disable_tag(self):
        pass

    def test_add_should_enable_tag(self):
        pass

    def test_iter_should_be_sorted_by_weight(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', label='Karen Duve',
                     weight='20')
        self.set_tag(content, id='Berlin', label='Berlin', weight='2')
        self.set_tag(content, id='Politik', label='Politik', weight='5')
        tagger = self.get_tagger(content)
        self.assertEqual(['Karen+Duve', 'Politik', 'Berlin'], list(tagger))

    def test_iter_should_sort_non_weighted_to_the_end(self):
        content = self.get_content()
        self.set_tag(content, id='Karen+Duve', label='Karen Duve',
                     weight='20')
        self.set_tag(content, id='Berlin', label='Berlin', weight='2')
        self.set_tag(content, id='Politik', label='Politik')
        tagger = self.get_tagger(content)
        self.assertEqual(['Karen+Duve', 'Berlin', 'Politik'], list(tagger))


class TestTag(zeit.cms.testing.FunctionalTestCase,
              unittest2.TestCase,
              TagTestHelpers):

    layer = zeit.intrafind.testing.layer

    def get_tag(self, code, **kw):
        from zeit.intrafind.tagger import Tag
        content = self.get_content()
        self.set_tag(content, code, **kw)
        return Tag(content, code)

    def test_tag_should_implement_interface(self):
        from zope.interface.verify import verifyObject
        from zeit.intrafind.interfaces import ITag
        self.assertTrue(
            verifyObject(ITag, self.get_tag('code', label='Label')))

    def test_tag_factory_should_return_none_if_there_is_no_label(self):
        self.assertIsNone(self.get_tag('code'))

    def test_tag_factory_should_return_tag_if_there_is_a_label(self):
        self.assertIsNotNone(self.get_tag('code', label='Label'))

    def test_label_should_be_readable_if_proxied(self):
        import zope.security.proxy
        tag = self.get_tag('Hamburg', label='Hamburg')
        tag.__parent__ = self.getRootFolder()
        proxied = zope.security.proxy.ProxyFactory(tag)
        self.assertEqual('Hamburg', proxied.label)

    def test_disabled_should_be_settable(self):
        from zeit.connector.interfaces import IWebDAVProperties
        tag = self.get_tag('Bielefeld', label='Bielefeld')
        tag.disabled = True
        dav = IWebDAVProperties(tag)
        self.assertIn(
            ('disabled', 'http://namespaces.zeit.de/CMS/tagging/Bielefeld'),
            dict(dav))
        self.assertEqual(
            'yes',
            dav[('disabled', 'http://namespaces.zeit.de/CMS/tagging/Bielefeld')])

    def test_same_code_should_have_same_hash(self):
        tag1 = self.get_tag('Rotterdam', label='Rotterdam')
        tag2= self.get_tag('Rotterdam', label="R'dam")
        self.assertEqual(hash(tag1), hash(tag2))

    def test_different_code_should_have_different_hash(self):
        tag1 = self.get_tag('Rotterdam', label='Rotterdam')
        tag2= self.get_tag("R'dam", label='Rotterdam')
        self.assertNotEqual(hash(tag1), hash(tag2))
