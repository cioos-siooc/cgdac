#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
glider_dac/views/user.py
View definitions for Users
'''
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from wtforms import validators, StringField, PasswordField, SubmitField
from wtforms.form import BaseForm

from glider_dac.app import app
from glider_dac.models import User
from glider_dac.models.shared_db import db


class UserForm(FlaskForm):
    username = StringField('Username')
    name = StringField('Name')
    password = PasswordField('Password', [
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    organization = StringField('Organization')
    email = StringField('Email')
    api_key = StringField('api_key')
    submit = SubmitField("Submit")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()

    if (form.is_submitted() and
            BaseForm.validate(form,
                              extra_validators={'password':
                                                    [validators.InputRequired()]})):
        user = User()
        form.populate_obj(user)
        user.save()

        flash(
            "Account for '%s' created, before you can login, your account needs to be approved by an admin" % user.username,
            'success')
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('register.html', form=form)


@app.route('/users/<string:username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    app.logger.info("GET %s", username)
    app.logger.info("Request URL: %s", request.url)
    user = User.query.filter_by(username=username).first()
    if user is None or (user is not None and not current_user.is_admin and current_user != user):
        # No permission
        app.logger.error("Permission is denied")
        app.logger.error("User: %s", user)
        app.logger.error("Admin?: %s", current_user.is_admin)
        app.logger.error("Not current user?: %s", current_user != user)
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    form = UserForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        flash("Account updated", 'success')
        return redirect(url_for("index"))

    return render_template('edit_user.html', form=form, user=user)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    form = UserForm()

    if (form.is_submitted() and
            BaseForm.validate(form,
                              extra_validators={'password':
                                                    [validators.InputRequired()]})):
        user = User()
        form.populate_obj(user)
        user.save()

        flash("Account for '%s' created" % user.username, 'success')
        return redirect(url_for("admin"))

    users = User.query.all()

    deployment_counts_raw = User.get_deployment_count_by_user()
    deployment_counts = {m['_id']: m['count'] for m in deployment_counts_raw}
    needs_approving = User.query.filter_by(is_approved=False).first() is not None

    return render_template('admin.html',
                           form=form,
                           users=users,
                           deployment_counts=deployment_counts,
                           needs_approving=needs_approving)


@app.route('/admin/<string:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    user = User.query.get(user_id)

    if not current_user.is_admin:
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    form = UserForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        flash("Account updated", 'success')
        return redirect(url_for("admin"))

    return render_template('edit_user.html', form=form, user=user)


@app.route('/admin/<string:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)

    if not current_user.is_admin:
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    if user.id == current_user.id:
        flash("You can't delete yourself!", "danger")
        return redirect(url_for("admin"))
    db.session.delete(user)
    db.session.commit()

    flash("User deleted", "success")
    return redirect(url_for('admin'))


# is_admin should be set to true/false
@app.route('/admin/<string:user_id>/is_admin/<string:is_admin>', methods=['POST'])
@login_required
def admin_change_user_admin(user_id, is_admin):
    user = User.query.get_or_404(user_id)
    is_admin = is_admin.lower() == 'true'
    if not current_user.is_admin:
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    # making sure there is at least 1 admin 
    if len(User.query.filter_by(is_admin=True).all()) == 1 and not is_admin:
        flash(f"Cannot unset admin for {user.username}, there needs to be at least one", "danger")
        return redirect(url_for('admin'))

    user.is_admin = is_admin
    db.session.commit()
    flash(f'User {user.username} has been changed to admin: {is_admin}', "success")
    return redirect(url_for('admin'))


@app.route('/admin/<string:user_id>/approve', methods=['POST'])
@login_required
def admin_approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_admin:
        # No permission
        flash("Permission denied", 'danger')
        return redirect(url_for("index"))

    user.is_approved = True
    db.session.commit()
    flash(f'User {user.username} has been approved', "success")
    return redirect(url_for('admin'))