# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~~~~

    Views callbacks.

"""

from flask import render_template, request, redirect, url_for, flash, jsonify

from app import app
from pop3accounts import POP3Info
from pop3messages import POP3Client


@app.route('/', methods=['GET', 'POST'])
def pop3_accounts_list():
    pop3 = POP3Info()
    accounts = pop3.get_accounts()
    return render_template('show_pop3_accounts.html', accounts=accounts)


@app.route('/account', methods=['GET', 'POST'])
def add_pop3_account():
    if request.method == 'POST': 
        pop3 = POP3Info()
        pop3.add_account(request.form['account'], request.form['hostname'],
                         request.form['passwd'], request.form['port'],
                         request.form['servername'])
        #flash('Added new account.')
        return redirect(url_for('pop3_accounts_list'))
    return render_template('set_pop3_account.html')


@app.route('/headers', methods=['GET', 'POST'])
def messages_headers():
    headers = []
    if request.method == 'POST': 
        pop3 = POP3Info()
        account = pop3.get_account(request.form['account'], request.form['hostname'])
        client = POP3Client(
            account.username, account.password,
            account.hostname, account.port)

        while (True):
            resp = client.connect()
            if resp != "OK":
                #flash('Bad connection status.')
                break
            resp = client.list()
            if resp != "OK":
                #flash('Bad command status.')
                break
            for header in client.msginfo():
                headers.append(header)
            break

        if resp != "OK":
            return redirect(url_for('pop3_accounts_list'))
    return render_template('show_pop3_messages.html', headers=headers)
