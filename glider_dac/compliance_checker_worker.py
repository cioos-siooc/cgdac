import sys
import os
import json
import logging
from glider_dac.models import Deployment
from glider_dac.backend_app import app

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
root_logger.addHandler(handler)


class ComplianceReportManager:
    def __init__(self, reports_home):
        self.reports_home = reports_home
        self._reports = []

    def discover_files_under_dir(self, file_dir: str) -> list:
        paths = []
        if os.path.isdir(file_dir):
            for file in os.listdir(file_dir):
                file_path = os.path.join(file_dir, file)
                if os.path.isfile(file_path):
                    paths.append(file_path)
        return paths

    def get_report_files(self) -> list:
        paths = []
        un_filter_paths = self.discover_files_under_dir(self.reports_home)
        for file_path in un_filter_paths:
            if file_path.endswith(".json"):
                paths.append(file_path)
        return paths

    def run(self):
        self.update_db()

    def update_db(self):
        summary_dict = self.analyze_reports()
        deployments = Deployment.query.all()
        root_logger.info("{} of deployments found".format(len(deployments)))
        root_logger.info(
            "{} of deployments compliance reports found in {}".format(len(summary_dict), self.reports_home))
        for deployment in deployments:
            dataset_id = deployment.name
            try:
                if dataset_id in summary_dict:
                    deployment.update(**summary_dict[dataset_id]["update_fields"])
                    
                    root_logger.info("Dateset {} is updated".format(dataset_id))
                else:
                    root_logger.info("Can't find {} in compliance checker report".format(dataset_id))
                
            except Exception as e:
                root_logger.error(e)
                root_logger.error("or maybe? unable to find the deployment {}".format(dataset_id))

    def analyze_reports(self):
        dataset_summary = dict()
        for report_path in self.get_report_files():
            file_name_with_ext = os.path.basename(report_path)
            file_name, ext = os.path.splitext(file_name_with_ext)
            dataset_id = file_name.rsplit("-", 1)[0]
            dataset_summary[dataset_id] = dict()
            with open(report_path, 'r') as f:
                errs = json.load(f)["gliderdac"]
                compliance_passed = errs['scored_points'] == errs['possible_points']

                update_fields = {"compliance_check_passed": compliance_passed}
                standard_name_errs = []
                if compliance_passed:
                    final_message = "All files passed compliance check on glider deployment {}".format(dataset_id)
                else:
                    update_fields["compliance_check_report"] = errs

                    for err in errs["high_priorities"]:
                        if err["name"] == "Standard Names":
                            standard_name_errs.extend(err["msgs"])

                    if not standard_name_errs:
                        final_message = "All files passed compliance check on glider deployment {}".format(dataset_id)
                    else:
                        final_message = ("Deployment {} has issues:\n{}".format(dataset_id,
                                                                                "\n".join(standard_name_errs)))
                dataset_summary[dataset_id]["final_message"] = final_message
                dataset_summary[dataset_id]["update_fields"] = update_fields
        return dataset_summary


def main():
    try:
        with app.app_context():
            ComplianceReportManager(app.config["COMPLIANCE_REPORTS_ROOT"]).run()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
