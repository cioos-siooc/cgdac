import json

from flask import request, make_response
from flask_cors import cross_origin

from glider_dac.models import Institution
from glider_dac.models.shared_db import db
from .utils import *

@app.route('/api/institution', methods=['GET'])
@cross_origin()
def get_institutions():
    institutions = [json.loads(inst.to_json()) for inst in Institution.query.all()]
    return jsonify(results=institutions)


@app.route('/api/institution', methods=['POST'])
@admin_required
@error_wrapper
def new_institution():
    app.logger.info(request.data)
    data = json.loads(request.data)
    institution = Institution()
    institution.name = data['name']
    db.session.add(institution)
    db.session.commit()
    return institution.to_json()


@app.route('/api/institution/<string:institution_id>', methods=['DELETE'])
@admin_required
@error_wrapper
def delete_institution(institution_id):
    if not current_user.is_admin:
        flash("Permission denied", 'danger')
        return redirect(url_for('index'))
    institution = Institution.query.get(institution_id)
    if institution is None:
        return jsonify({}), 404
    app.logger.info("Deleting institution")
    db.session.delete(institution)
    db.session.commit()
    return make_response(jsonify({}), 204)
