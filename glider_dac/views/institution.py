#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
glider_dac/views/institution.py
View definition for institutions
'''
import json

from flask import render_template, redirect, flash, url_for, jsonify, request
from flask_cors import cross_origin
from flask_login import current_user

from wtforms import StringField, SubmitField
from functools import wraps

from glider_dac.app import app
from flask_wtf import FlaskForm


from glider_dac.models import Institution
from glider_dac.models.shared_db import db

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


class NewInstitutionForm(FlaskForm):
    name = StringField('Institution Name')
    submit = SubmitField('New Institution')


@app.route('/institutions/', methods=['GET', 'POST'])
@admin_required
def show_institutions():
    institutions = list(Institution.query.all())
    form = NewInstitutionForm()
    if form.validate_on_submit():
        institution = Institution()
        institution.name = form.name.data
        db.session.add(institution)
        db.session.commit()
        flash('Institution Created', 'success')

    return render_template('institutions.html',
                           form=form,
                           institutions=institutions)

