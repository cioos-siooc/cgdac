import re
import json
import os
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse as dateparse
from multidict import CIMultiDict


from flask import jsonify, request, make_response
from flask_restx import Resource

from .api_init import api
from glider_dac.models import Deployment, User
from glider_dac.views.operation.deployment import new_deployment_creation
from .api_parsers import deployment_get_parser, deployment_post_parser, deployment_file_get_parser, \
    deployment_file_post_parser

def parse_date(datestr):
    from cf_units import Unit
    '''
    Parse the time query param
    '''
    try:
        if datestr.startswith('now-'):
            p = re.compile(r'^now-(?P<val>\d+)\s*(?P<units>\w+)$')
            match = p.search(datestr)
            val = int(match.group('val'))
            units = match.group('units')
            # If not valid units, exception will throw
            unknown_unit = Unit(units)
            hrs = Unit('hours')
            # convert to hours
            num_hrs = unknown_unit.convert(val, hrs)
            dt_now = datetime.now(tz=timezone.utc)
            return dt_now - timedelta(hours=num_hrs)

        return dateparse(datestr)
    except Exception:
        return None

def verification(username, api_key):
    ret = False
    user = User.query.filter_by(username=username).first()
    if user and user.api_key == api_key and user.is_approved:
        ret = True
    return ret


@api.doc(responses={
    200: 'Success',
    201: 'Created',
    400: 'Validation Error',
    500: 'Internal Server Error',
    501: 'Not Implemented'
})
@api.route('/deployment_file/', endpoint='deployment_file')
class DeploymentFileApi(Resource):

    @api.expect(deployment_file_post_parser)
    @api.doc(security='apikey')
    def post(self):
        parse_args = deployment_file_post_parser.parse_args()
        username = parse_args.get("username", None)
        deployment_name = parse_args.get("deployment_name", None)
        files = parse_args['file']
        try:
            api_key = request.headers["X-API-KEY"]
            verification(username, api_key)
        except Exception:
            api.abort(403)
            return
        deployment = Deployment.query.filter_by(name=deployment_name).first()
        user = User.query.filter_by(username=username).first()

        if not (deployment and user and deployment.user_id == user.id):
            raise Exception("Unauthorized")  # @TODO better response via ajax?
        file_name = files.filename
        out_name = os.path.join(deployment.full_path, file_name)
        try:
            with open(out_name, 'wb') as of:
                files.save(of)
        except Exception:
            pass

        return 'OK', 201

    @api.expect(deployment_file_get_parser)
    @api.doc(security='apikey')
    def get(self):
        parse_args = deployment_file_get_parser.parse_args()
        username = parse_args.get("username", None)
        deployment_name = parse_args.get("deployment_name", None)
        try:
            api_key = request.headers["X-API-KEY"]
            verification(username, api_key)
        except Exception:
            api.abort(403)
            return
        user = User.query.filter_by(username=username).first()
        deployment = Deployment.query.filter_by(name=deployment_name, user_id=user.id).first()
        files = []
        for dirpath, _dirnames, filenames in os.walk(deployment.full_path):
            for f in filenames:
                if f.endswith('.nc'):
                    files.append((f, datetime.utcfromtimestamp(
                        os.path.getmtime(os.path.join(dirpath, f)))))

        files.sort(key=lambda a: a[1])
        return jsonify(files)


@api.route('/deployment/')
class DeploymentApi(Resource):
    '''
    API endpoint to fetch deployment info
        ---
    parameters:
      - in: query
        name: completed
        required: false
        schema:
          type: boolean
        description: >
          Filter datasets by the completed attribute
      - in: query
        name: delayed_mode
        required: false
        schema:
          type: boolean
        description: >
          Filter datasets by the delayed_mode attribute
      - in: query
        name: minTime
        required: false
        schema:
          type: string
        example: now-12hr
        description: >
          Filter datasets with by last file's modtime being newer than minTime.
          Enter a datetime string (yyyy-MM-ddTHH:mm:ssZ)
          Or specify 'now-nUnits' for example now-12hr (integers only!)
    responses:
        200:
          description: Success
        400:
          description: Bad Request
        500:
          description: Internal Server Error
        501:
          description: Not Implemented
    '''

    def get_deployment_by_username_deployment_name(self, username, deployment_name):
        deployment = Deployment.query.filter_by(
            username=username, name=deployment_name).first()
        if deployment is None:
            return make_response(jsonify(message='No record found'), 204)
        d = json.loads(deployment.to_json(ignore_fields=['id','user_id']))
        d['erddap'] = deployment.erddap
        d['attribution'] = deployment.attribution
        d['created'] = {"$date" : d['created']}
        d['latest_file_mtime'] = {"$date" : d['latest_file_mtime']}
        d['updated'] = {"$date" : d['updated']}
        return jsonify(**d)

    @api.doc(security='apikey')
    @api.expect(deployment_post_parser)
    def post(self):

        parse_args = deployment_post_parser.parse_args()
        username = parse_args.get("username", None)
        glider_name = parse_args.get("deployment_name", None)
        deployment_date = parse_date(parse_args.get("deployment_date", None))
        delayed_mode = parse_args.get("delayed_mode", None)
        attribution = parse_args.get("attribution", None)
        wmo_id = parse_args.get("wmo_id", None)
        try:
            api_key = request.headers["X-API-KEY"]
            verification(username, api_key)
        except Exception:
            api.abort(403)
            return

        new_deployment_creation(username,
                                glider_name,
                                deployment_date,
                                delayed_mode,
                                attribution=attribution,
                                wmo_id=wmo_id)

    @api.expect(deployment_get_parser)
    def get(self):
        parse_args = deployment_get_parser.parse_args()
        username = parse_args.get("username", None)
        deployment_name = parse_args.get("deployment_name", None)
        if username and deployment_name:
            return self.get_deployment_by_username_deployment_name(username, deployment_name)
        # Parse case insensitive query parameters
        request_query = CIMultiDict(request.args)

        # Get the query values
        deployments = Deployment.query
        completed = request_query.get('completed', None)
        if completed and completed.lower() in ['true', 'false']:
            deployments = deployments.filter_by(completed=(completed.lower() == 'true'))

        delayed_mode = request_query.get('delayed_mode', None)
        if delayed_mode and delayed_mode.lower() in ['true', 'false']:
            deployments = deployments.filter_by(delayed_mode=(delayed_mode.lower() == 'true'))

        min_time = request_query.get('minTime', None)
        if min_time:
            min_time_dt = parse_date(min_time)
            if min_time_dt is not None:
                deployments = deployments.filter(Deployment.latest_file_mtime >= min_time_dt)

        deployments = deployments.all()
        results = []
        for deployment in deployments:
            d = json.loads(deployment.to_json(ignore_fields=['id','compliance_check_report','user_id']))
            d['erddap'] = deployment.erddap
            d['attribution'] = deployment.attribution
            d['created'] = {"$date" : d['created']}
            d['latest_file_mtime'] = {"$date" : d['latest_file_mtime']}
            d['updated'] = {"$date" : d['updated']}
            results.append(d)

        return jsonify(results=results, num_results=len(results))
