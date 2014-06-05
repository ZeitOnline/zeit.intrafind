# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.httpserverlayer.custom
import pkg_resources
import zeit.cms.testing


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    response_code = 200
    response_body = None
    default_response = '<?xml version="1.0"?><tagResults/>'
    posts_received = []

    def do_POST(self):
        length = int(self.headers['content-length'])
        self.posts_received.append(dict(
            path=self.path,
            data=self.rfile.read(length),
        ))
        self.send_response(self.response_code)
        self.end_headers()
        self.wfile.write(self.response_body or self.default_response)


class HTTPLayer(gocept.httpserverlayer.custom.Layer):

    def testTearDown(self):
        super(HTTPLayer, self).testTearDown()
        self['request_handler'].posts_received[:] = []
        self['request_handler'].response_body = None
        self['request_handler'].response_code = 200

HTTP_LAYER = HTTPLayer(
    RequestHandler, name='HTTPLayer', module=__name__)


product_config = """
<product-config zeit.intrafind>
    tagger http://localhost:[PORT]/ZeitOnline/tagger
    trisolute-url file://{egg}/tests/fixtures/googleNewsTopics.json
    trisolute-ressort-url file://{egg}/tests/fixtures/trisolute-ressorts.xml
</product-config>
""".format(egg=pkg_resources.resource_filename(__name__, ''))


class ZCMLLayer(zeit.cms.testing.ZCML_Layer):

    defaultBases = (HTTP_LAYER,)

    def setUp(self):
        self.product_config = self.product_config.replace(
            '[PORT]', str(self['http_port']))
        super(ZCMLLayer, self).setUp()


ZCML_LAYER = ZCMLLayer('ftesting.zcml', product_config=product_config)
