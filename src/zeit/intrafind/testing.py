# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.testing


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

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

    @classmethod
    def tearDown(cls):
        cls.posts_received[:] = []
        cls.response_body = None
        cls.response_code = 200


tagger_layer, http_port = zeit.cms.testing.HTTPServerLayer(RequestHandler)

product_config = """
    <product-config zeit.intrafind>
        tagger http://localhost:{port}/ZeitOnline/tagger
        trisolute-url file://{egg}/tests/fixtures/googleNewsTopics.json
    </product-config>
""".format(port=http_port, egg=pkg_resources.resource_filename(__name__, ''))


zcml_layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml',
                                        product_config=product_config)


class layer(tagger_layer,
            zcml_layer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass

