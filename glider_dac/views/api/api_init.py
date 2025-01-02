from flask import Blueprint
from flask_restx import Api, Resource
from glider_dac.app import app, csrf

blueprint = Blueprint('api', __name__, url_prefix='/api')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}
api = Api(blueprint, doc='/doc/', authorizations=authorizations)
csrf.exempt(blueprint)
app.register_blueprint(blueprint)