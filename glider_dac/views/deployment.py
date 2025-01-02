#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
glider_dac/views/deployment.py
View definition for Deployments
'''
import re
import json
import os

from cf_units import Unit
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse as dateparse
from flask import render_template, redirect, jsonify, flash, url_for, request, Markup
from flask_cors import cross_origin
from flask_wtf import FlaskForm
from flask_login import login_required, current_user

from glider_dac.glider_emails import send_registration_email
from multidict import CIMultiDict
from pymongo.errors import DuplicateKeyError
from wtforms import StringField, SubmitField, BooleanField, validators
from glider_dac.backend_app import app
from glider_dac.models.shared_db import db
from glider_dac.models import User, Deployment
from glider_dac.views.operation.deployment import new_deployment_creation

def is_date_parseable(form, field):
    try:
        dateparse(field.data)
    except ValueError:
        raise validators.ValidationError("Invalid Date")


def is_valid_glider_name(form, field):
    regex = r'^[a-zA-Z]+[a-zA-Z0-9-_]*$'
    if not re.match(regex, field.data):
        raise validators.ValidationError("Invalid Glider Name")


def deployment_key_fn(dep):
    """
    Helper function for sorting deployments.  Returns the "updated" attribute
    timestamp (defaulting to 1970-01-01 if not found), followed by the
    deployment name as the sorting key.
    """
    default_dt = datetime(1970, 1, 1)
    return getattr(dep, 'updated', default_dt), dep.name


class DeploymentForm(FlaskForm):
    operator = StringField('Operator')
    completed = BooleanField('Completed')
    archive_safe = BooleanField("Submit to NCEI on Completion")
    attribution = StringField('Attribution')
    submit = SubmitField('Submit')


class NewDeploymentForm(FlaskForm):
    glider_name = StringField('Glider Name', [is_valid_glider_name])
    deployment_date = StringField('Deployment Date', [is_date_parseable])
    attribution = StringField('Attribution')
    delayed_mode = BooleanField('Delayed Mode?')
    submit = SubmitField("Create")


@app.route('/users/<string:username>/deployments')
def list_user_deployments(username):
    user = User.query.filter_by(username=username).first()
    deployments = Deployment.query.filter_by(user_id=user.id).all()

    kwargs = {}
    if current_user and current_user.is_active and (current_user.is_admin or
                                                    current_user.id == user.id):
        # Permission to edit
        form = NewDeploymentForm()
        kwargs['form'] = form

    for m in deployments:
        if not os.path.exists(m.full_path):
            continue

        m.updated = datetime.utcfromtimestamp(os.path.getmtime(m.full_path))

    deployments = Deployment.query.filter_by(user_id=user.id).order_by(Deployment.updated).all()

    return render_template('user_deployments.html', username=username,
                           deployments=deployments, **kwargs)


@app.route('/operators/<path:operator>/deployments')
def list_operator_deployments(operator):
    deployments = Deployment.query.filter_by(operator=str(operator)).all()

    for m in deployments:
        if not os.path.exists(m.full_path):
            continue

        m.updated = datetime.utcfromtimestamp(os.path.getmtime(m.full_path))

    deployments = Deployment.query.filter_by(operator=str(operator)).order_by(Deployment.updated).all()

    return render_template('operator_deployments.html', operator=operator, deployments=deployments)


@app.route('/users/<string:username>/deployment/<string:deployment_id>')
def show_deployment(username, deployment_id):
    user = User.query.filter_by(username= username).first()
    deployment = Deployment.query.get(deployment_id)

    files = []
    for dirpath, _dirnames, filenames in os.walk(deployment.full_path):
        for f in filenames:
            if f.endswith('.nc'):
                files.append((f, datetime.utcfromtimestamp(
                    os.path.getmtime(os.path.join(dirpath, f)))))

    files.sort(key=lambda a: a[1])

    kwargs = {}

    form = DeploymentForm(obj=deployment)

    if current_user and current_user.is_active and (current_user.is_admin or
                                                    current_user.id == user.id):
        kwargs['editable'] = True
        if current_user.is_admin or current_user.id == user.id:
            kwargs['admin'] = True

    deployment_json = json.loads(deployment.to_json())
    return render_template('show_deployment.html', username=username, form=form, deployment=deployment_json, files=files, **kwargs)


@app.route('/deployment/<string:deployment_id>')
def show_deployment_no_username(deployment_id):
    deployment = Deployment.query.get(deployment_id)
    username = User.query.get(deployment.user_id).username
    return redirect(url_for('show_deployment', username=username, deployment_id=deployment.id))


@app.route('/users/<string:username>/deployment/new', methods=['POST'])
@login_required
def new_deployment(username):
    user = User.query.filter_by(username=username).first()
    if user is None or (user is not None and not current_user.is_admin and
                        current_user != user):
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    form = NewDeploymentForm()

    if form.validate_on_submit():
        deployment_date = dateparse(form.deployment_date.data)
        delayed_mode = form.delayed_mode.data
        new_deployment_creation(username, form.glider_name.data, deployment_date, delayed_mode,attribution=form.attribution.data)
    else:
        error_str = ", ".join(["%s: %s" % (k, ", ".join(v))
                               for k, v in form.errors.items()])
        flash("Deployment could not be created: %s" % error_str, 'danger')

    return redirect(url_for('list_user_deployments', username=username))


@app.route('/users/<string:username>/deployment/<string:deployment_id>/new',
           methods=['POST'])
@login_required
def new_delayed_mode_deployment(username, deployment_id):
    '''
    Endpoint for submitting a delayed mode deployment from an existing
    realtime deployment

    :param string username: Username
    :param ObjectId deployment_id: Id of the existing realtime deployment
    '''
    user = User.query.filter_by(username=username).first()
    if user is None or (user is not None and not current_user.is_admin and
                        current_user != user):
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    rt_deployment = Deployment.query.get(deployment_id)
    # Need to check if the "real time" deployment is complete yet
    if not rt_deployment.completed:
        deployment_url = url_for('show_deployment', username=username, deployment_id=deployment_id)
        flash(Markup('The real time deployment <a href="%s">%s</a> must be marked as complete before adding delayed mode data' %
              (deployment_url, rt_deployment.name)), 'danger')
        return redirect(url_for('list_user_deployments', username=username))

    new_deployment_creation(username, rt_deployment.name, rt_deployment.deployment_date, rt_deployment.attribution, rt_deployment.operator,  rt_deployment.wmo_id)

    return redirect(url_for('list_user_deployments', username=username))

@app.route('/users/<string:username>/deployment/<string:deployment_id>/edit', methods=['POST'])
@login_required
def edit_deployment(username, deployment_id):

    user = User.query.filter_by(username= username).first()
    if user is None or (user is not None and not current_user.is_admin and
                        current_user != user):
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for('list_user_deployments', username=username))

    deployment = Deployment.query.get(deployment_id)

    form = DeploymentForm(obj=deployment)

    if form.validate_on_submit():
        form.populate_obj(deployment)
        deployment.updated = datetime.utcnow()
        db.session.commit()
        flash("Deployment updated", 'success')
        return redirect(url_for('show_deployment', username=username, deployment_id=deployment.id))
    else:
        error_str = ", ".join(["%s: %s" % (k, ", ".join(v))
                               for k, v in form.errors.items()])
        flash("Deployment could not be edited: %s" % error_str, 'danger')

    return render_template('edit_deployment.html', username=username, form=form, deployment=deployment)


@app.route('/users/<string:username>/deployment/<string:deployment_id>/files', methods=['POST'])
@login_required
def post_deployment_file(username, deployment_id):

    deployment = Deployment.query.get(deployment_id)
    user = User.query.filter_by(username=username).first()

    if not (deployment and user and deployment.user_id == user.id and
            (current_user.is_admin or current_user.id == user.id)):
        raise Exception("Unauthorized")  # @TODO better response via ajax?

    retval = []
    for name, f in request.files.items():
        if not name.startswith('file-'):
            continue

        safe_filename = f.filename  # @TODO

        out_name = os.path.join(deployment.full_path, safe_filename)

        try:
            with open(out_name, 'wb') as of:
                f.save(of)
        except Exception:
            app.logger.exception('Error uploading file: {}'.format(out_name))

        retval.append((safe_filename, datetime.utcnow()))
    editable = current_user and current_user.is_active and (
        current_user.is_admin or current_user == user)

    return render_template("_deployment_files.html", files=retval, editable=editable)


@app.route('/users/<string:username>/deployment/<string:deployment_id>/delete_files', methods=['POST'])
@login_required
def delete_deployment_files(username, deployment_id):

    deployment = Deployment.query.get(deployment_id)
    user = User.query.filter_by(username= username).first()
    if deployment is None:
        # @TODO better response via ajax?
        raise Exception("Unauthorized")
    if user is None:
        # @TODO better response via ajax?
        raise Exception("Unauthorized")
    if not (current_user and current_user.is_active and (current_user.is_admin
                                                         or current_user.id ==
                                                         user.id)):
        # @TODO better response via ajax?
        raise Exception("Unauthorized")

    if not (deployment and user and (current_user.is_admin or user.id ==
                                     deployment.user_id)):
        # @TODO better response via ajax?
        raise Exception("Unauthorized")

    for name in request.json['files']:
        file_name = os.path.join(deployment.full_path, name)
        os.unlink(file_name)

    return ""


@app.route('/users/<string:username>/deployment/<string:deployment_id>/delete', methods=['POST'])
@login_required
def delete_deployment(username, deployment_id):

    deployment = Deployment.query.get(deployment_id)
    user = User.query.filter_by(username= username).first()
    if deployment is None:
        flash("Permission denied", 'danger')
        return redirect(url_for("show_deployment", username=username, deployment_id=deployment_id))
    if user is None:
        flash("Permission denied", 'danger')
        return redirect(url_for("show_deployment", username=username, deployment_id=deployment_id))
    if not (current_user and current_user.is_active and (current_user.is_admin
                                                         or current_user.id ==
                                                         user.id)):
        flash("Permission denied", 'danger')
        return redirect(url_for("show_deployment", username=username, deployment_id=deployment_id))
    db.session.delete(deployment)
    db.session.commit()
    flash("Deployment queued for deletion", 'success')

    return redirect(url_for("list_user_deployments", username=username))
