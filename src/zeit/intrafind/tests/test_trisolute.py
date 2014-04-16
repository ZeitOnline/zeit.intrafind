# coding: utf-8
import zeit.cms.testing
import zeit.intrafind.testing
import zope.component


class GoogleNewsTopics(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.intrafind.testing.zcml_layer

    @property
    def topics(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.ICurrentTopics)

    def test_parses_response_into_data_dict(self):
        self.assertEqual(
            u'Europäisches Parlament', self.topics('Wirtschaft')[0])

    def test_headlines_are_not_keywords(self):
        self.assertIn(u'FC Liverpool', self.topics.headlines)
        self.assertNotIn(u'FC Liverpool', self.topics())

    def test_no_ressort_given_returns_all_keywords(self):
        self.assertEqual(u'Europäisches Parlament', self.topics()[0])

    def test_unknown_ressort_returns_empty_list(self):
        self.assertEqual([], self.topics('Unknown'))

    def test_ressorts_are_mapped_to_categories(self):
        self.assertIn('YouTube', self.topics('Mobilitaet'))