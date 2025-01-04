import os

from datetime import datetime
from dateutil.parser import parse as dateparse
from flask import redirect, flash, url_for

from flask_login import current_user

# from glider_dac.glider_emails import send_registration_email

from glider_dac.models import User, Deployment


def new_deployment(username):
    user = User.query.filter_by(username=username).first()
    if user is None or (user is not None and not current_user.is_admin and
                        current_user.id != user.id):
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    form = NewDeploymentForm()

    if form.validate_on_submit():
        deployment_date = dateparse(form.deployment_date.data)
        delayed_mode = form.delayed_mode.data
        deployment_name = form.glider_name.data + '-' + \
                          deployment_date.strftime('%Y%m%dT%H%M')
        if delayed_mode:
            deployment_name += '-delayed'

        try:

            existing_deployment = Deployment.query.filter_by(name=deployment_name).first()
            if existing_deployment is None:
                print()
            else:
                raise DuplicateKeyError("Duplicate Key Detected: name")
            existing_deployment = Deployment.query.filter_by(
                glider_name=form.glider_name.data, deployment_date=deployment_date).first()
            if existing_deployment is None:
                deployment = Deployment()
                deployment.user_id = user.id
                deployment.username = username
                deployment.deployment_dir = os.path.join(username, deployment_name)
                deployment.updated = datetime.utcnow()
                deployment.deployment_date = deployment_date
                deployment.glider_name = form.glider_name.data
                deployment.name = deployment_name
                deployment.attribution = form.attribution.data
                deployment.delayed_mode = delayed_mode

                deployment.save()
                flash("Deployment created", 'success')
                send_registration_email(username, deployment)
            else:
                # if there is a previous real-time deployment and the one
                # to create is marked as delayed mode, act as if the delayed
                # mode modification path had been followed
                if not existing_deployment.delayed_mode and delayed_mode:
                    return new_delayed_mode_deployment(username,
                                                       existing_deployment._id)
        except DuplicateKeyError:
            flash("Deployment names must be unique across Glider DAC: %s already used" %
                  deployment_name, 'danger')

    else:
        error_str = ", ".join(["%s: %s" % (k, ", ".join(v))
                               for k, v in form.errors.items()])
        flash("Deployment could not be created: %s" % error_str, 'danger')

    return redirect(url_for('list_user_deployments', username=username))


def _deployment_creation(user, glider_name, deployment_date, deployment_name, delayed_mode, attribution=None,
                         operator=None, wmo_id=None):
    deployment = Deployment()
    deployment.user_id = user.id
    deployment.username = user.username
    deployment.deployment_dir = os.path.join(user.username, deployment_name)
    deployment.updated = datetime.utcnow()
    deployment.deployment_date = deployment_date
    deployment.glider_name = glider_name
    deployment.name = deployment_name
    if attribution:
        deployment.attribution = attribution
    if operator:
        deployment.operator = operator
    if wmo_id:
        deployment.wmo_id = wmo_id
    deployment.delayed_mode = delayed_mode

    deployment.save()
    flash("Deployment created", 'success')
    # send_registration_email(user.username, deployment)


def new_deployment_creation(username, glider_name, deployment_date, delayed_mode, attribution=None, operator=None,
                            wmo_id=None):
    user = User.query.filter_by(username=username).first()
    deployment_name = glider_name + '-' + \
                      deployment_date.strftime('%Y%m%dT%H%M')
    if delayed_mode:
        deployment_name += '-delayed'
    existing_deployment = Deployment.query.filter_by(name=deployment_name).first()
    if existing_deployment is not None:
        if not existing_deployment.delayed_mode and delayed_mode:
            # if there is a previous real-time deployment and the one
            # to create is marked as delayed mode, act as if the delayed
            # mode modification path had been followed
            if not attribution:
                attribution = existing_deployment.attribution
                operator = existing_deployment.operator
                wmo_id = existing_deployment.wmo_id
        flash("Deployment names must be unique across Glider DAC: %s already used" %
              deployment_name, 'danger')
    else:
        _deployment_creation(user, glider_name, deployment_date, deployment_name, delayed_mode, attribution, operator,
                             wmo_id)
