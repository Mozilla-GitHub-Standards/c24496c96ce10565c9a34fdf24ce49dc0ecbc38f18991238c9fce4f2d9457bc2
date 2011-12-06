from cStringIO import StringIO
from webtest import TestApp
from webob.dec import wsgify
from webtestrecorder import Recorder, get_records, write_doctest, write_function_unittest
from nose.tools import eq_

@wsgify
def demo_application(req):
    return 'test response'

def test_recorder():
    out = StringIO()
    app = TestApp(Recorder(demo_application, file=out))
    app.get('/test')
    app.post('/example', {'var': 'value'})
    data = out.getvalue()
    records = get_records(StringIO(data))
    result = StringIO()
    write_doctest(records, result)
    dt = result.getvalue()
    print dt
    eq_(dt, doctest_example)
    result = StringIO()
    write_function_unittest(records, result)
    test = result.getvalue()
    print test
    eq_(test, function_unittest_example)

doctest_example = """\
    >>> print app.get('/test')
    Response: 200 OK
    Content-Type: text/html; charset=UTF-8
    test response
    >>> print app.post('/example', params=dict(var=u'value'))
    Response: 200 OK
    Content-Type: text/html; charset=UTF-8
    test response
"""

function_unittest_example = """\
from webtest import TestApp

def test_app():
    app = TestApp(application)
    resp = app.get('/test')
    assert resp.body == 'test response'
    resp = app.post('/example', params=dict(var=u'value'))
    assert resp.body == 'test response'
"""
