# -*- coding: utf-8 -*-
"""
    app.pop3messages
    ~~~~~~~~~~~~

    File contains simplified pop3 client implementation for
    getting list of headers for pointed pop3 account

"""

import re
import socket
from poplib import POP3, error_proto
from itertools import imap

import helpers

DEFAULT_PORT = 110
CONN_TIMEOUT = 3

class POP3Client():
    """POP3 client wrapper for getting specific header information"""

    def __init__(self, user, passwd, host, port=DEFAULT_PORT):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.pop3 = None
        self.rstatus = re.compile("^\+OK")
        self.mails = []

    def connect(self):
        """POP3 clien connection call."""
        error = None
        try:
            self.pop3 = POP3(self.host, self.port, CONN_TIMEOUT)
        except (socket.error, socket.herror,
            socket.gaierror, socket.timeout) as error:
            return error.strerror
        except error_proto:
            return error
        except Exception:
            return "Internal error!"

        resp = self.pop3.user(self.user)
        if not self.rstatus.search(resp):
            return resp

        resp = self.pop3.pass_(self.passwd)
        if not self.rstatus.search(resp):
            return resp
        return "OK"

    def list(self):
        """Store list of available message ids on the server."""
        resp, self.mails, octets = self.pop3.list()
        if not self.rstatus.search(resp):
            return resp
        return "OK"

    def headers(self):
        for id in imap(lambda x: x.split(' ')[0], self.mails):
            resp, header, octets = self.pop3.top(id, 0)
            if not self.rstatus.search(resp):
                continue
            yield header

    def msginfo(self):
        """Get tuple of header information, including sender, 
        subject and submit/receive date of the message. Function
        works as a generator.
        """
        i = 0
        for id in imap(lambda x: x.split(' ')[0], self.mails):
            resp, header, octets = self.pop3.top(id, 0)
            if not self.rstatus.search(resp):
                continue
            yield helpers.parse_header(id, header, ++i%2)

    def quit(self):
        if self.pop3:
            self.pop3.quit()
