import sys
import os
import json
import tempfile
import logging

from datetime import datetime
from collections import OrderedDict

from flask_mail import Message
from flask import render_template

from compliance_checker.suite import CheckSuite
from compliance_checker.runner import ComplianceChecker
from glider_dac.app import app, mail, db
from glider_dac.models import Deployment, User



root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
root_logger.addHandler(handler)

def send_notification(username, deployment):
    if not app.config.get('MAIL_ENABLED', False):  # Mail is disabled
        app.logger.info("Email is disabled")
        return
    else:
        send_registration_email(username, deployment)

def send_registration_email(username, deployment):
    if not app.config.get('MAIL_ENABLED', False): # Mail is disabled
        app.logger.info("Email is disabled")
        return
    # sender comes from MAIL_DEFAULT_SENDER in env
    app.logger.info("Sending email about new deployment to %s", app.config.get('MAIL_DEFAULT_TO'))
    subject        = "New Glider Deployment - %s" % deployment.name
    recipients     = [app.config.get('MAIL_DEFAULT_TO')]
    cc_recipients  = []
    if app.config.get('MAIL_DEFAULT_LIST') is not None:
        cc_recipients.append(app.config.get('MAIL_DEFAULT_LIST'))

    msg            = Message(subject, recipients=recipients, cc=cc_recipients)
    msg.body       = render_template(
                        'deployment_registration.txt',
                        deployment=deployment,
                        username=username,
                        thredds_url=get_thredds_catalog_url(),
                        erddap_url=get_erddap_catalog_url())

    mail.send(msg)

def send_deployment_cchecker_email(user, failing_deployments, attachment_msgs):
    if not app.config.get('MAIL_ENABLED', False): # Mail is disabled
        app.logger.info("Email is disabled")
        return
    # sender comes from MAIL_DEFAULT_SENDER in env

    app.logger.info("Sending email about deployment compliance checker to {}".format(user['username']))
    subject        = "Glider DAC Compliance Check on Deployments for user %s" % user['username']
    recipients     = [user['email']] #app.config.get('MAIL_DEFAULT_TO')]
    msg            = Message(subject, recipients=recipients)
    if len(failing_deployments) > 0:
        message = ("The following glider deployments failed compliance check:"
                   "\n{}\n\nPlease see attached file for more details. "
                   "Valid CF standard names are required for NCEI archival."
                   .format("\n".join(d['name'] for d in failing_deployments)))
        date_str_today = datetime.today().strftime("%Y-%m-%d")
        attachment_filename = "failing_glider_md_{}".format(date_str_today)
        msg.attach(attachment_filename, 'text/plain', data=attachment_msgs)
    else:
        return
    msg.body       = message

    mail.send(msg)

def get_thredds_catalog_url():
    args = {
        'host' : app.config['THREDDS']
    }
    url = 'http://%(host)s/thredds/catalog.xml' % args
    return url

def get_erddap_catalog_url():
    args = {
        'host' : app.config['PUBLIC_ERDDAP']
    }
    url = 'http://%(host)s/erddap/metadata/iso19115/xml/' % args
    return url


def process_deployment(dep):
    deployment_issues = "Deployment {}".format(os.path.basename(dep['name']))
    groups = OrderedDict()
    erddap_fmt_string = "erddap/tabledap/{}.nc?&time%3Emax(time)-1%20day"
    base_url = app.config["PRIVATE_ERDDAP"]
    # FIXME: determine a more robust way of getting scheme
    if not base_url.startswith("http"):
        base_url = "http://{}".format(base_url)
    url_path = "/".join([base_url,
                         erddap_fmt_string.format(dep["name"])])
    # TODO: would be better if we didn't have to write to a temp file
    outhandle, outfile = tempfile.mkstemp()
    failures, _ = ComplianceChecker.run_checker(ds_loc=url_path,
                                  checker_names=['gliderdac'], verbose=True,
                                  criteria='lenient', output_format='json',
                                  output_filename=outfile)
    with open(outfile, 'r') as f:
        errs = json.load(f)["gliderdac"]

    compliance_passed = errs['scored_points'] == errs['possible_points']

    update_fields = {"compliance_check_passed": compliance_passed}
    standard_name_errs = []
    if compliance_passed:
        final_message = "All files passed compliance check on glider deployment {}".format(dep['name'])
    else:
        error_list = [err_msg for err_severity in ("high_priorities",
            "medium_priorities", "low_priorities") for err_section in
            errs[err_severity] for err_msg in err_section["msgs"]]
        update_fields["compliance_check_report"] = errs

        for err in errs["high_priorities"]:
            if err["name"] == "Standard Names":
                standard_name_errs.extend(err["msgs"])

        if not standard_name_errs:
            final_message = "All files passed compliance check on glider deployment {}".format(dep['name'])
        else:
            root_logger.info(standard_name_errs)
            final_message = ("Deployment {} has issues:\n{}".format(dep['name'],
                             "\n".join(standard_name_errs)))

    # Set fields.  Don't use upsert as deployment ought to exist prior to write.
    db.deployments.update({"_id": dep["_id"]}, {"$set": update_fields})
    return final_message.startswith("All files passed"), final_message
