from __future__ import absolute_import
import mock
import pyramid_dogpile_cache2
import zeit.cms.testing
import zope.component


class TestWhitelist(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super(TestWhitelist, self).setUp()
        pyramid_dogpile_cache2.clear()

    def whitelist(self):
        from ..whitelist import Whitelist
        return Whitelist()

    def test_get_url_should_use_cms_product_config(self):
        wl = self.whitelist()
        with mock.patch(
                'zope.app.appsetup.product.getProductConfiguration') as gpc:
            wl._get_url()
        gpc.assert_called_with('zeit.cms')

    def test_fetch_should_load_url_from_get_url(self):
        wl = self.whitelist()
        wl._get_url = mock.Mock(return_value=mock.sentinel.url)
        with mock.patch('urllib2.urlopen') as urlopen:
            wl._fetch()
        urlopen.assert_called_with(mock.sentinel.url)

    def test_fetch_should_return_urlopen_result(self):
        wl = self.whitelist()
        wl._get_url = mock.Mock(return_value=mock.sentinel.url)
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = mock.sentinel.response
            self.assertEqual(mock.sentinel.response, wl._fetch())

    def test_load_should_xml_parse_fetch_result(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock(return_value=mock.sentinel.response)
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            wl._load()
        fromfile.assert_called_with(mock.sentinel.response)

    def test_load_should_iterate_tag_nodes(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock(return_value=mock.sentinel.response)
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            wl._load()
        fromfile().xpath.assert_called_with('//tag')

    def test_load_should_create_tag_for_tag_nodes(self):
        wl = self.whitelist()
        with mock.patch('zeit.intrafind.tag.Tag') as Tag:
            wl._load()
        self.assertEqual(55, Tag.call_count)
        Tag.assert_called_with(
            'ae11024e-69e0-4434-b7d3-f66efddb0459', u'Polarkreis',
            entity_type=None, url_value=None),

    def test_load_should_set_entity_type_if_present(self):
        wl = self.whitelist()
        wl._load()
        self.assertEqual(
            'Person',
            wl.get('221da83c-427a-417f-81e2-0d8b1c65b669').entity_type)

    def test_get_retrieves_tag_via_uuid(self):
        wl = self.whitelist()
        wl._load()
        self.assertEqual(
            'Polarkreis', wl.get('ae11024e-69e0-4434-b7d3-f66efddb0459').label)

    def test_get_returns_None_if_uuid_does_not_match(self):
        wl = self.whitelist()
        wl._load()
        self.assertEqual(None, wl.get('I-do-not-match'))

    def test_load_should_add_tags_to_whitelist(self):
        wl = self.whitelist()
        wl._load()
        self.assertEqual(55, len(wl.search('')))

    def test_accessing_data_attribute_should_trigger_load(self):
        wl = self.whitelist()
        wl._load = mock.Mock(return_value={})
        wl.data
        self.assertTrue(wl._load.called)

    def test_load_result_should_be_cached(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock()
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            fromfile.reset_mock()
            wl._load()
            wl._load()
        self.assertEqual(1, fromfile.call_count)


class TestTopicpages(zeit.cms.testing.ZeitCmsTestCase):

    layer = zeit.intrafind.testing.ZCML_LAYER

    def test_converts_whitelist_to_topic_dicts(self):
        wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
        wl._load()
        topics = zope.component.getUtility(
            zeit.cms.tagging.interfaces.ITopicpages)
        result = topics.get_topics()
        self.assertEqual('testtag', result[0]['id'])
        self.assertEqual('Testtag', result[0]['title'])
