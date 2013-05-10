# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~~~~

    Views callbacks.

"""

from flask import render_template, request, \
    redirect, url_for, flash, jsonify
from flask.ext.wtf import Form, TextField, \
    validators, PasswordField, IntegerField, SubmitField
from wtforms.validators import ValidationError

from app import app
from pop3accounts import POP3Info
from pop3messages import POP3Client


### Used form definitions ###
def HostNameCheck(form, field):
    if len(field.data.split('.')) == 1:
        raise ValidationError('Incorrect hostname format')


class MngAccountForm(Form):
    account = TextField("Username:",
        [validators.InputRequired(message="Account field is obligatory"),
         validators.Length(max=40, message="Account name is too long")])
    hostname = TextField("Hostname or IPv4:",
        [validators.InputRequired(message="Hostname field is obligatory"),
         validators.Length(max=20, message="Hostname is too long"),
         HostNameCheck])
    port = IntegerField("Port number:",
        [validators.NumberRange(min=1, max=65535, message="Incorrect port number")],
        default=110)


class AddAccountForm(MngAccountForm):
    servername = TextField("Server description:",
        [validators.Length(max=40, message="Server name is too long")])
    passwd = PasswordField("Password:",
        [validators.InputRequired(message="Password field is obligatory"),
         validators.Length(max=20, message="Password is too long")])
    submit = SubmitField("Submit")


### Routing callbacks ###
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


@app.route('/delaccount', methods=['GET'])
def del_pop3_account():
    user = request.args.get('username', '', type=str)
    host = request.args.get('hostname', '', type=str)
    port = "110"

    try:
        host, port = host.index(":")
    except ValueError:
        pass
    pop3 = POP3Info()
    rc = pop3.del_account(user, host, port)
    print "HERE", user, host, port, rc
    return jsonify(result=rc)


@app.route('/testaccount', methods=['GET'])
def test_pop3_account():
    user = request.args.get('username', '', type=str)
    host = request.args.get('hostname', '', type=str)
    port = "110"

    try:
        host, port = host.index(":")
    except ValueError:
        pass
    pop3 = POP3Info()
    account = pop3.get_account(user, host, port)
    client = POP3Client(
            account.username, account.password,
            account.hostname, account.port)
    rc = client.connect()
    return jsonify(result=rc)


@app.route('/headers', methods=['GET', 'POST'])
def messages_headers():
    form = MngAccountForm()
    headers = []
    if form.validate_on_submit():
        pop3 = POP3Info()
        account = pop3.get_account(
            form.account.data, form.hostname.data, form.port.data)
        client = POP3Client(
            account.username, account.password,
            account.hostname, account.port)

        while (True):
            result = client.connect()
            if result != "OK":
                break
            result = client.list()
            if result != "OK":
                break
            for header in client.msginfo():
                headers.append(header)
            break

        if result != "OK":
            flash("Getting headers for '{0}' account on '{1}' failed: {2}".format(
                form.account.data, form.hostname.data, result), 'error')
            return redirect(url_for('pop3_accounts_list'))
    return render_template('show_pop3_messages.html', headers=headers)
