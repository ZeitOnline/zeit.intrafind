from zeit.cms.application import CONFIG_CACHE
import collections
import gocept.lxml.objectify
import logging
import lxml.etree
import urllib2
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.intrafind.tag
import zope.interface


log = logging.getLogger(__name__)


def xpath_lowercase(context, x):
    return x[0].lower()
xpath_functions = lxml.etree.FunctionNamespace('zeit.intrafind')
xpath_functions['lower'] = xpath_lowercase


class Whitelist(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    @property
    def data(self):
        return self._load()

    def search(self, term):
        xml = self._fetch()
        nodes = xml.xpath(
            '//tag[contains(zeit:lower(text()), "%s")]' %
            term.lower(), namespaces={'zeit': 'zeit.intrafind'})
        return [self.get(x.get('uuid')) for x in nodes]

    def locations(self, term):
        return [
            tag for tag in self.search(term) if tag.entity_type == 'Location']

    def get(self, id):
        result = self.data.get(id)
        return result if result else None

    @CONFIG_CACHE.cache_on_arguments()
    def _fetch(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        url = config.get('whitelist-url')
        log.info('Loading keyword whitelist from %s', url)
        data = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(data)

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        xml = self._fetch()
        tags = collections.OrderedDict()
        for tag_node in xml.xpath('//tag'):
            tag = zeit.intrafind.tag.Tag(
                tag_node.get('uuid'), unicode(tag_node).strip(),
                entity_type=tag_node.get('type'),
                url_value=tag_node.get('url_value'))
            tags[tag.code] = tag
        log.info('Keywords loaded.')
        return tags


class Topicpages(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITopicpages)

    def get_topics(self, start=0, rows=25):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        result = zeit.cms.interfaces.Result()
        result.hits = len(whitelist.data)
        for tag in whitelist.data.values()[start:start + rows]:
            result.append({
                'id': tag.url_value,
                'title': tag.label,
            })
        return result
