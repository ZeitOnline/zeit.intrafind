from zeit.cms.application import CONFIG_CACHE
import collections
import gocept.lxml.objectify
import logging
import urllib2
import zeit.cms.tagging.interfaces
import zeit.intrafind.tag
import zope.interface


log = logging.getLogger(__name__)


class Whitelist(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    @property
    def data(self):
        return self._load()

    def search(self, term):
        term = term.lower()
        return [tag for tag in self.data.values() if term in tag.label.lower()]

    def get(self, id):
        result = self.data.get(id)
        return result if result else None

    def _get_url(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        return cms_config.get('whitelist-url')

    def _fetch(self):
        url = self._get_url()
        __traceback_info__ = (url,)
        log.info('Loading keyword whitelist from %s', url)
        return urllib2.urlopen(url)

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        tags = collections.OrderedDict()
        tags_xml = gocept.lxml.objectify.fromfile(self._fetch())
        for tag_node in tags_xml.xpath('//tag'):
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
        result = zeit.cms.tagging.interfaces.Result()
        result.hits = len(whitelist.data)
        for tag in whitelist.data.values()[start:start + rows]:
            result.append({
                'id': tag.url_value,
                'title': tag.label,
            })
        return result
