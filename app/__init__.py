import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql://' + app.config['DBADMIN'] + ':' + app.config['DBPASS'] + \
    '@' + app.config['DBHOST'] + '/'

if not os.environ.get('CINFO_TESTING'):
    app.config['SQLALCHEMY_DATABASE_URI'] += app.config['DBNAME']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] += app.config['DBTESTNAME']

db = SQLAlchemy(app)

from app import views
