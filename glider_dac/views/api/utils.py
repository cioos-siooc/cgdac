from functools import wraps

from flask import redirect, flash, url_for
from flask_login import current_user
from flask import jsonify

from glider_dac.app import app




def error_wrapper(func):
    '''
    Function wrapper to catch exceptions and return them as jsonified errors
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify(error=type(e).__name__, message=e.message), 500

    return wrapper


def admin_required(func):
    '''
    Wraps a route to require an administrator
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        elif not current_user.is_admin:
            flash("Permission denied", 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)

    return wrapper
