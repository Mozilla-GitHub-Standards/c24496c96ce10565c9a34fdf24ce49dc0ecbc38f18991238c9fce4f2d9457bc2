import os
import httplib
from wsgiproxy.exactproxy import proxy_exact_request


def replay_records(records, host=None, methods=None):
    for req in records:
        if host:
            if ':' in host:
                req.server_name, req.server_port = host.split(':', 1)
            else:
                req.server_name = host
                req.server_port = '80'
            req.host = host
        if methods:
            if req.method not in methods:
                yield req, None
        n = 0
        resp = None
        while 1:
            try:
                resp = req.get_response(proxy_exact_request)
                break
            except httplib.HTTPException:
                if n >= 3:
                    break
                n += 1
        if resp is not None:
            yield req, resp


def main():
    import sys
    import optparse
    from webtestrecorder.apachelog import parse_apache_log, apache_log_line
    parser = optparse.OptionParser(
        usage='%prog FILENAMES --filter CODE')
    parser.add_option(
        '--filter', action='append',
        metavar='CODE',
        help='Code to run on each request, should define a function "f"; '
        'may return None to filter out, or modify the request')
    parser.add_option(
        '--host', metavar='HOST',
        help='Override the request host')
    parser.add_option(
        '--GET', action='store_true',
        help='Only run GET requests')
    parser.add_option(
        '--print-response', action='store_true',
        help='Show the response')
    parser.add_option(
        '--failures', metavar='FILE',
        help="write all failures to the given file")
    parser.add_option(
        '--success', metavar='FILE',
        help="write all succeeding URLs to the given file (as Apache log lines)")
    options, args = parser.parse_args()
    if not args:
        fps = [sys.stdin]
    else:
        fps = [open(fn) for fn in args]
    if options.filter:
        filters = parse_filters(options.filter)
    else:
        filters = None
    if options.failures:
        failures = open(options.failures, 'a')
    else:
        failures = None
    if options.success:
        success = open(options.success, 'a')
    else:
        success = None
    records = []
    for fp in fps:
        for req in parse_apache_log(fp):
            if options.filter:
                req = run_filters(filters, req)
                if req:
                    records.append(req)
            else:
                records.append(req)
    if options.GET:
        methods = ['GET']
    else:
        methods = None
    for req, resp in replay_records(records, methods=methods,
                                    host=options.host):
        if not resp:
            print 'Skipped request %s %s' % (req.method, req.path_qs)
        else:
            print '%s %s' % (req.method, req.path_qs)
            if req.response and req.response.status_int != resp.status_int:
                print resp
                print '  -> %s (originally %s)' % (resp.status, req.response.status_int)
                if failures:
                    failures.write(
                        ('%s %s\n' % (req.method, req.path_qs)) +
                        ('  -> %s %s (originally %s)\n' % (resp.status, resp.location or '', req.response.status_int)))
            else:
                if options.print_response:
                    print resp
                if success:
                    success.write(apache_log_line(req, resp) + '\n')


def parse_filters(filters):
    f = []
    for index, filter_code in enumerate(filters):
        fn = 'arg-%s' % (index + 1)
        if os.path.exists(filter_code):
            fn = filter_code
            fp = open(filter_code)
            filter_code = fp.read()
            fp.close()
        ns = {'__file__': fn}
        exec filter_code in ns
        if 'f' not in ns:
            raise Exception('No function f() in code:\n%s' % filter_code)
        f.append(ns['f'])
    return f


def run_filters(filters, req):
    for f in filters:
        req = f(req)
        if not req:
            return None
    return req

if __name__ == '__main__':
    main()
