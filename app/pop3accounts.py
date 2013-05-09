# -*- coding: utf-8 -*-
"""
    app.pop3accounts
    ~~~~~~~~~~~~

    File contains pop3 accounts model and related management class.

"""
from collections import namedtuple

from app import db

class Servers(db.Model):
    """POP3 server information, where hostname and port fields pair are
    unique. Not default port number is set only. Additional optional
    'description' field provides brief server name/description
    """
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(20), index=True, unique= True, nullable=False)
    port = db.Column(db.Integer, default=110)
    description = db.Column(db.String(40))
    iserver = db.Index('iserver', 'hostname', 'port', unique=True)


class Eboxes(db.Model):
    """POP3 account information are bound to the corresponding POP3 server
    via 'server_id' foeign key and provides authentication data (apop auth
    type is not supported here).
    """
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    srv = db.relationship(
        'Servers', backref=db.backref('accounts', cascade="all,delete"),
        single_parent=True)
    user = db.Column(db.String(40), index=True, nullable=False)
    passwd = db.Column(db.String(20), nullable=False)


class POP3Info():
    """Class provides management of pop3 accounts."""

    def get_accounts(self, limit=20, offset=0):
        """Retrieve subset of stored pop3 accounts.

        :param limit: number of records per request
        :param offset: offset in the sorted contacts storage
        :returns: list of tuples, which represent pop3
        accounts information
        """
        if not db.session.query(Servers, Eboxes).\
            outerjoin(Servers.accounts).first():
            return []

        _query = db.session.query(Servers, Eboxes).\
            outerjoin(Servers.accounts).\
            limit(limit).offset(offset)

        _info = namedtuple('_info', 'description hostname username id')
        _result = []
        for _i, _data in enumerate(_query.all()):
           if _data[0].port and _data[0].port != 110:
               _data[0].hostname += ':' + str(_data[0].port)

           _result.append(_info(
               description = _data[0].description if _data[0].description else '',
               hostname = _data[0].hostname,
               username = _data[1].user,
               id=_i))

        return _result

    def get_account(self, user, host, port):
        """Retrieve pop3 account, if it is present.

        :user: account name or mail address
        :host: host name or IPv4 address
        :port: port number
        :returns: tuple of account info or None, if absent
        """
        _data = self._get_account(user, host, port=110)
        if not _data:
            return None

        _info = namedtuple('_info', 'username, password, hostname, port')
        return _info(
            username = user, password = _data[1].passwd,
            hostname = host, port = port)

    def add_account(self, user, host, passwd, port=None, description=None):
        """Add pop3 account.

        :user: account name or mail address
        :host: host name or IPv4 address
        :passwd: plaintext account password
        :port: port number, if not default value
        :description: server name/description, if present
        :returns: True, if success.
        """
        if self._get_account(user, host, port):
            return False

        _server = self._get_host(host, port)
        if not _server:
            _server = Servers(hostname=host)
        _account = Eboxes(user=user, passwd=passwd)
        if description:
            _server.description = description
        if port:
            _server.port = port

        _server.accounts.append(_account)
        db.session.add(_server)
        db.session.commit()
        return True

    def del_account(self, user, host, port=None):
        """Delete pop3 account.

        :user: account name or mail address
        :host: host name or IPv4 address
        :port: port number, if not default value
        :returns: True, if success.
        """
        _data = self._get_account(user, host, port)
        if not _data:
            return False

        db.session.delete(_data[1])
        #If account references absent, delete host entry too
        if db.session.query(Servers, Eboxes).\
            outerjoin(Servers.accounts).\
            filter(Servers.hostname == host).\
            filter(Servers.port == port).\
            first():
            db.session.delete(_data[0])
        db.session.commit()
        return True

    def _get_account(self, user, host, port=None):
        return db.session.query(Servers, Eboxes).\
            outerjoin(Servers.accounts).\
            filter(Servers.hostname == host).\
            filter(Servers.port == port).\
            filter(Eboxes.user == user).\
            first()

    def _get_host(self, host, port=None):
        return db.session.query(Servers).\
            filter(Servers.hostname == host).\
            filter(Servers.port == port).\
            first()
