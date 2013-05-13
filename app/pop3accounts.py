# -*- coding: utf-8 -*-
"""
    app.pop3accounts
    ~~~~~~~~~~~~

    File contains pop3 accounts model and related management class.

"""
from collections import namedtuple
from sqlalchemy import and_

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
            join(Servers.accounts).first():
            return []

        query = db.session.query(Servers, Eboxes).\
            join(Servers.accounts).\
            limit(limit).offset(offset)

        info = namedtuple('info', 'description hostname username id')
        result = []
        for i, data in enumerate(query.all()):
           if data[0].port and data[0].port != 110:
               data[0].hostname += ':' + str(data[0].port)

           result.append(info(
               description = data[0].description if data[0].description else '',
               hostname = data[0].hostname,
               username = data[1].user,
               id=i))

        return result

    def get_account(self, user, host, port):
        """Retrieve pop3 account, if it is present.

        :user: account name or mail address
        :host: host name or IPv4 address
        :port: port number
        :returns: tuple of account info or None, if absent
        """
        data = self._get_account(user, host, port=110)
        if not data:
            return None

        info = namedtuple('info', 'username, password, hostname, port')
        return info(
            username = user, password = data[1].passwd,
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

        server = self._get_host(host, port)
        if not server:
            server = Servers(hostname=host)
        account = Eboxes(user=user, passwd=passwd)
        if description:
            server.description = description
        if port:
            server.port = port

        server.accounts.append(account)
        db.session.add(server)
        db.session.commit()
        return True

    def del_account(self, user, host, port=None):
        """Delete pop3 account.

        :user: account name or mail address
        :host: host name or IPv4 address
        :port: port number, if not default value
        :returns: True, if success.
        """
        data = self._get_account(user, host, port)
        if not data:
            return False

        #If host contains the only account references,
        #it must be deleted too
        count = db.session.query(Servers, Eboxes).join(Servers.accounts).\
            filter(and_(Servers.hostname == host, Servers.port == port)).count()

        if count > 1:
            db.session.delete(data[1])
        else:
            db.session.delete(data[0])
        db.session.commit()
        return True

    def _get_account(self, user, host, port=None):
        return db.session.query(Servers, Eboxes).join(Servers.accounts).\
            filter(and_(Servers.hostname == host, Servers.port == port,
                Eboxes.user == user)).first()

    def _get_host(self, host, port=None):
        return db.session.query(Servers).filter(and_(Servers.hostname == host,
            Servers.port == port)).first()
