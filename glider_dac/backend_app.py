"""
initializing everything needed for the backend processing
"""
from flask import Flask
from flask_session import Session
from flask_migrate import Migrate
from common.config import *

"""
Flask app initialize
"""
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'CGDAC',
    'uiversion': 3,
    'openapi': '3.0.2'
}

from glider_dac.models.shared_db import db

app.config.update(DICT_CONFIG)

POSTGRES_USER = app.config["POSTGRES_USER"]
POSTGRES_PW = app.config["POSTGRES_PASSWORD"]
POSTGRES_DB = app.config["POSTGRES_DATABASE"]
POSTGRES_HOST = app.config["POSTGRES_HOST"]

if app.config["USE_SQLITE_OVER_POSTGRES"]:
    # Define the path for the SQLite database file
    db_folder = check_create_dir(os.path.join(app.config["RESOURCE_FOLDER"], "db"))  # Example: ./data/db.sqlite3
    db_path = os.path.join(db_folder, "db.sqlite3")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

else:
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW,
                                                                   url=POSTGRES_HOST, db=POSTGRES_DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db.init_app(app)
migrate = Migrate(app, db)

app.config["SESSION_TYPE"] = 'sqlalchemy'
app.config["SESSION_SQLALCHEMY"] = db
Session(app)

with app.app_context():
    db.create_all()
