from flasgger import LazyString, LazyJSONEncoder
from flask import request
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from glider_dac.reverse_proxy import ReverseProxied
from glider_dac.common import log_formatter
from glider_dac.backend_app import *
from glider_dac.utils import *

csrf = CSRFProtect()
app.url_map.strict_slashes = False
app.wsgi_app = ReverseProxied(app.wsgi_app)

csrf.init_app(app)
app.config['SWAGGER'] = {
    'title': 'glider-dac',
    'uiversion': 3,
    'openapi': '3.0.2'
}
app.json_encoder = LazyJSONEncoder
template = dict(swaggerUiPrefix=LazyString(lambda: request.environ.get('HTTP_X_SCRIPT_NAME', '')))

# Login manager for frontend
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User Auth DB file - create if not existing

# Create logging
if app.config.get('LOG_FILE') == True:
    import logging
    from logging import FileHandler

    file_handler = FileHandler(os.path.join(os.path.dirname(__file__),
                                            '../logs/glider_dac.txt'))
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Application Process Started')

# Create datetime jinja2 filter

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['timedeltaformat'] = timedeltaformat
app.jinja_env.filters['prettydate'] = prettydate
app.jinja_env.filters['pluralize'] = pluralize
app.jinja_env.filters['padfit'] = padfit

# Import everything
import glider_dac.models
import glider_dac.views
