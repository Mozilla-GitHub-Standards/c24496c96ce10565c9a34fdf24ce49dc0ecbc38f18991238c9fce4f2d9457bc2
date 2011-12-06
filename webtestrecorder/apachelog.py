import re
from datetime import datetime
from webob import Request, Response

apache_regex = re.compile(
    r'''
    (?P<remote_host>[^\s]+) \s+
    (?P<remote_ident>[^\s]+) \s+
    (?P<remote_user>[^\s]+) \s+
    \[ (?P<date>[^\]]*) \] \s+
    " (?P<method>[A-Z]+) \s+
      (?P<path>[^\s]+) \s+
      (?P<http_version>[^"]+) " \s+
    (?P<status>\d+) \s+
    (?P<size>\d+) \s+
    " (?P<referrer>[^"]+) " \s+
    " (?P<user_agent>[^"]+) "
    ''',
    re.VERBOSE)


def parse_apache_log(fp, host='localhost',
                     RequestClass=Request, ResponseClass=Response):
    for line in fp:
        line = line.strip()
        if not line:
            continue
        match = apache_regex.match(line)
        if not match:
            continue
        d = match.groupdict()
        for key in d:
            if d[key] == '-':
                d[key] = None
        req = RequestClass.blank(
            d['path'],
            host=host,
            method=d['method'],
            referrer=d['referrer'],
            user_agent=d['user_agent'],
            )
        req.date = parse_apache_date(d['date'])
        if d['remote_user']:
            req.environ['REMOTE_USER'] = d['remote_user']
        if d['remote_host']:
            req.environ['REMOTE_HOST'] = d['remote_host']
        req.environ['HTTP_PROTOCOL'] = d['http_version']
        resp = ResponseClass('\0' * int(d['size'] or 0),
                             status=d['status'])
        req.response = resp
        yield req

line_template = (
    '%(REMOTE_HOST)s %(REMOTE_IDENT)s %(REMOTE_USER)s '
    '[%(date)s] "%(REQUEST_METHOD)s %(path)s %(HTTP_PROTOCOL)s" '
    '%(status)s %(size)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"')


def apache_log_line(req, resp):
    d = {}
    for var in ['REMOTE_HOST', 'REMOTE_IDENT', 'REMOTE_USER',
                'HTTP_REFERER', 'HTTP_USER_AGENT',
                'REQUEST_METHOD', 'HTTP_PROTOCOL']:
        if req.environ.get(var):
            d[var] = req.environ[var].replace('"', '')
        else:
            d[var] = '-'
    d['date'] = req.date.strftime('%d/%b/%Y:%H:%M:%S')
    d['path'] = req.path_qs
    d['status'] = resp.status
    d['size'] = resp.content_length or '-'
    return line_template % d


def parse_apache_date(date):
    return datetime.strptime(date.split()[0], '%d/%b/%Y:%H:%M:%S')
