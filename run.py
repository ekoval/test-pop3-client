import os, sys

sys.path.insert(0, os.getcwd())
from app import app, db

db.create_all()        # For testing purposes, if table exists, skipped

app.run(debug = True, host='0.0.0.0')
