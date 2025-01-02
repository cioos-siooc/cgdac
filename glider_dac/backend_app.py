"""
initializing everything needed for the dac_backend processing
"""

import os
import yaml
from flask import Flask
from flask_session import Session
from flask_migrate import Migrate
""""
Path initialize and config
"""
cur_dir = os.path.dirname(__file__)
with open(os.path.join(cur_dir, '..', 'config.yml')) as base_config:
    config_dict = yaml.load(base_config, Loader=yaml.Loader)

extra_config_path = os.path.join(cur_dir, '..', 'config.local.yml')
# merge in settings from config.local.yml, if it exists
if os.path.exists(extra_config_path):
    with open(extra_config_path) as extra_config:
        config_dict = {**config_dict, **yaml.load(extra_config,
                                                  Loader=yaml.Loader)}

#############################

"""
Flask app initialize
"""
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'glider-dac',
    'uiversion': 3,
    'openapi': '3.0.2'
}

if app.config["ENV"].upper() == "PRODUCTION":
    try:
        app.config.update(config_dict["PRODUCTION"])
    except KeyError:
        app.config.update(config_dict["DEVELOPMENT"])
else:
    app.config.update(config_dict["DEVELOPMENT"])


from glider_dac.models.shared_db import db
POSTGRES_USER = app.config.get("POSTGRES_USER")
POSTGRES_PW = app.config.get("POSTGRES_PASSWORD")
POSTGRES_DB = app.config.get("POSTGRES_DATABASE")
POSTGRES_HOST = app.config.get("POSTGRES_HOST")

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_HOST,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)
migrate = Migrate(app, db)

app.config["SESSION_TYPE"] = 'sqlalchemy'
app.config["SESSION_SQLALCHEMY"] = db
Session(app)

with app.app_context():
    db.create_all()

"""
load the userDB
"""

if not os.path.exists(app.config.get('USER_DB_FILE')):
    from glider_util.bdb import UserDB

    UserDB.init_db(app.config.get('USER_DB_FILE'))
