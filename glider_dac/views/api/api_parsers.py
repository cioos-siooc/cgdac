from .api_init import api
from werkzeug.datastructures import FileStorage
deployment_get_parser = api.parser()
deployment_get_parser.add_argument('username', type=str, help='Name of the user')
deployment_get_parser.add_argument('deployment_name', type=str, help="The name of the deployment")
deployment_get_parser.add_argument('minTime', type=str, help="The minimum deployment date format YYY-MM-DD")

deployment_post_parser = api.parser()
deployment_post_parser.add_argument('username', type=str, help='Name of the user', required=True)
deployment_post_parser.add_argument('deployment_name', type=str, help="The name of the deployment", required=True)
deployment_post_parser.add_argument('deployment_date', type=str, help="The deployment date format YYY-MM-DD", required=True)
deployment_post_parser.add_argument('delayed_mode', type=bool, help="is this is delayed mode.")
deployment_post_parser.add_argument('attribution', type=str, help="The attribution of the deployment.")
deployment_post_parser.add_argument('wmo_id', type=str, help="The WMO ID of the glider.")

deployment_file_get_parser = api.parser()
deployment_file_get_parser.add_argument('username', type=str, help='Name of the user', required=True)
deployment_file_get_parser.add_argument('deployment_name', type=str, help='The name of the deployment', required=True)


deployment_file_post_parser = api.parser()
deployment_file_post_parser.add_argument('username', type=str, help='Name of the user', required=True)
deployment_file_post_parser.add_argument('deployment_name', type=str, help='The name of the deployment', required=True)
deployment_file_post_parser.add_argument('file', location='files', type=FileStorage, required=True)