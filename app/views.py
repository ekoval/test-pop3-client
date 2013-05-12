# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~~~~

    Views callbacks.

"""
import socket
from poplib import error_proto

from flask import render_template, \
    redirect, url_for, flash, jsonify
from flask.ext.wtf import Form, TextField, \
    validators, PasswordField, IntegerField, \
    SubmitField, HiddenField
from wtforms.validators import ValidationError

from app import app
from pop3accounts import POP3Info
from pop3messages import POP3Client, jsonify_response


### Used form definitions.
def HostNameCheck(form, field):
    if len(field.data.split('.')) == 1:
        raise ValidationError('Incorrect hostname format')


class MngAccountForm(Form):
    account = HiddenField('Username:',
        [validators.InputRequired(message='Account field is obligatory'),
         validators.Length(max=40, message='Account name is too long')])
    hostname = HiddenField('Hostname or IPv4:',
        [validators.InputRequired(message='Hostname field is obligatory'),
         validators.Length(max=20, message='Hostname is too long'),
         HostNameCheck])
    port = IntegerField('Port number:',
        [validators.NumberRange(min=1, max=65535, message='Incorrect port number')],
        default=110)


class TestForm(MngAccountForm):
    passwd = PasswordField('Password:',
        [validators.InputRequired(message='Password field is obligatory'),
         validators.Length(max=20, message='Password is too long')])


class AddAccountForm(Form):
    account = TextField('Username:',
        [validators.InputRequired(message='Account field is obligatory'),
         validators.Length(max=40, message='Account name is too long')])
    hostname = TextField('Hostname or IPv4:',
        [validators.InputRequired(message='Hostname field is obligatory'),
         validators.Length(max=20, message='Hostname is too long'),
         HostNameCheck])
    port = IntegerField('Port number:',
        [validators.NumberRange(min=1, max=65535, message='Incorrect port number')],
        default=110)
    servername = TextField('Server description:',
        [validators.Length(max=40, message='Server name is too long')])
    passwd = PasswordField('Password:',
        [validators.InputRequired(message='Password field is obligatory'),
         validators.Length(max=20, message='Password is too long')])
    submit = SubmitField('Submit')


### Routing callbacks.
@app.route('/', methods=['GET'])
def pop3_accounts_list():
    pop3 = POP3Info()
    accounts = pop3.get_accounts()
    return render_template('show_pop3_accounts.html', accounts=accounts)


@app.route('/addaccount', methods=['GET', 'POST'])
def add_pop3_account():
    form = AddAccountForm(csrf_enabled=False)
    if form.validate_on_submit():
        pop3 = POP3Info()
        result = pop3.add_account(form.account.data, form.hostname.data,
            form.passwd.data, form.port.data,
            form.servername.data)
        if result:
            flash("Added account '{0}' for '{1}'!".format(
                form.account.data, form.hostname.data), 'info')
        else:
            flash("'Account {0}' for '{1} already exists'!".format(
                form.account.data, form.hostname.data), 'error')
        return redirect(url_for('pop3_accounts_list'))
    return render_template('set_pop3_account.html', form=form)


@app.route('/delaccount', methods=['POST'])
def del_pop3_account():
    form = MngAccountForm(csrf_enabled=False)
    if form.validate_on_submit():
        pop3 = POP3Info()
        result = pop3.del_account(
            form.account.data, form.hostname.data, form.port.data)
        if result:
            flash("Deleted account '{0}' for '{1}'!".format(
                form.account.data, form.hostname.data), 'info')
        else:
            flash("'Account {0}' for '{1} does not exist'!".format(
                form.account.data, form.hostname.data), 'error')
    else:
        flash('Not valid form data!', 'error')
    return redirect(url_for('pop3_accounts_list'))


@app.route('/headers', methods=['GET', 'POST'])
def messages_headers():
    form = MngAccountForm(csrf_enabled=False)
    headers = []
    if form.validate_on_submit():
        pop3 = POP3Info()
        account = pop3.get_account(
            form.account.data, form.hostname.data, form.port.data)
        client = POP3Client(
            account.username, account.password,
            account.hostname, account.port)
        result = None
        try:
            client.connect()
            client.list()
            for header in client.msginfo():
                headers.append(header)
        except error_proto as error:
            result = str(error)
        except socket.error as error:
            result = 'host connection error!'
        except (socket.herror, socket.gaierror) as error:
            result = 'host addressing error!'
        except socket.timeout as error:
            result = 'host timeout error!'
        if result:
            flash("Getting headers for '{0}' account on '{1}' failed: {2}".format(
                form.account.data, form.hostname.data, result), 'error')
            return redirect(url_for('pop3_accounts_list'))
    else:
        flash("Not valid form data!", 'error')
        return render_template('show_pop3_accounts.html')
    return render_template('show_pop3_messages.html', headers=headers)


@app.route('/testaccount', methods=['POST'])
def test_pop3_account():
    form = TestForm(csrf_enabled=False)
    if form.validate_on_submit():
        client = POP3Client(
            form.account.data, form.passwd.data,
            form.hostname.data, form.port.data)
        client.connect()
        return jsonify(result='OK')
    elif form.port.errors:
        return jsonify(result=form.port.errors[0])
    else:
        return jsonify(result='Not valid form data!')


### Pop3 client error handlers assignements exclusively
### for test_pop3_account() AJAX request.
@app.errorhandler(error_proto)
@jsonify_response
def pop3_protocol_error(error):
    return str(error)


@app.errorhandler(socket.error)
@jsonify_response
def pop3_socket_error(error):
    return 'Host connection error!'


@app.errorhandler(socket.herror)
@jsonify_response
def pop3_addressing_error(error):
    return 'Host addressing error!'


@app.errorhandler(socket.timeout)
@jsonify_response
def pop3_timeout_error(error):
    return 'Host timeout error!'
