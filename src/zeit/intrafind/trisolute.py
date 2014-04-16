import gocept.cache.method
import itertools
import json
import logging
import urllib2
import zeit.cms.tagging.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class GoogleNewsTopics(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ICurrentTopics)

    def __call__(self, ressort=None):
        if ressort is None:
            return list(itertools.chain(*self.keywords.values()))
        return self.keywords.get(ressort, [])

    @property
    def headlines(self):
        return self.headlines

    @property
    def keywords(self):
        self._load()
        return self._keywords

    @property
    def headlines(self):
        self._load()
        return self._headlines

    @gocept.cache.method.Memoize(600, ignore_self=True)
    def _load(self):
        log.debug('Retrieving %s', self._trisolute_url)
        response = urllib2.urlopen(self._trisolute_url, timeout=60)
        data = json.loads(response.read())
        keywords = {}
        headlines = []
        for category in data:
            if category['headlineCategory'] == 'Schlagzeilen':
                headlines = category['topics']
            else:
                keywords[category['headlineCategory']] = category['topics']
        self._keywords = keywords
        self._headlines = headlines

    @property
    def _trisolute_url(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.intrafind')
        return config['trisolute-url']
