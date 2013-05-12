# -*- coding: utf-8 -*-
"""
    app.pop3messages
    ~~~~~~~~~~~~

    File contains simplified pop3 client implementation for
    getting list of headers for pointed pop3 account

"""

import re
import functools
from poplib import POP3
from collections import namedtuple
from itertools import imap

from flask import jsonify

DEFAULT_PORT = 110
CONN_TIMEOUT = 3

#Interesting mail headers by categories in the descending order
#from the point of view of more strict correspondence of
#requirements.
SNDR_HDRS = ['From:', 'Sender:', 'Originator:', 'Return-Path:']
SUBJ_HDRS = ['Subject:', 'Keywords:', 'Comments:', 'Summary:']
DATE_HDRS = ['Date:', 'Delivery-Date:', 'Received:']

def _parse_header(header, keys):
    """Internal helper function for parse_header() call"""
    for entry in header:
        regexes = [ re.compile(pattern + " *(.*$)") for pattern in keys ]
        for regex in regexes:
            match = regex.search(entry)
            if match:
                return match.group(1)


def parse_header(msgid, header, odd):
    """Helper function, which return named tuple of three fields,
    ('sender', 'subject', 'date'), from received header.
    """
    _sender = _parse_header(header, SNDR_HDRS)
    _subject = _parse_header(header, SUBJ_HDRS)
    _date = _parse_header(header, DATE_HDRS)
    regex = re.compile("\(.*\); *(.*$)")
    _found = regex.search(_date)
    if _found and _found.group(1):
        _date = _found.group(1)

    _headinfo = namedtuple('_headinfo', 'msgid, odd, sender, subject, date')
    return _headinfo(msgid=msgid, odd=odd,sender=_sender,
                     subject=_subject, date=_date)


class POP3Client():
    """POP3 client wrapper for getting specific header information"""

    def __init__(self, user, passwd, host, port=DEFAULT_PORT):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.pop3 = None
        self.mails = []

    def connect(self):
        """POP3 clien connection call."""
        self.pop3 = POP3(self.host, self.port, CONN_TIMEOUT)
        self.pop3.user(self.user)
        self.pop3.pass_(self.passwd)


    def list(self):
        """Store list of available message ids on the server."""
        resp, self.mails, octets = self.pop3.list()

    def msginfo(self):
        """Get tuple of header information, including sender, 
        subject and submit/receive date of the message. Function
        works as a generator.
        """
        i = 0
        for id in imap(lambda x: x.split(' ')[0], self.mails):
            resp, header, octets = self.pop3.top(id, 0)
            yield parse_header(id, header, ++i%2)

    def quit(self):
        if self.pop3:
            self.pop3.quit()


def jsonify_response(func):
    """Decorator, which jsonify function returned value
    in special manner.
    """
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        return jsonify({'result': func(*args, **kwargs)})
    return decorated_view
