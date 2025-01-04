import os
import glob
import hashlib
from datetime import datetime
from shutil import rmtree

from glider_dac.backend_app import app
from glider_dac.utils import slugify

from glider_dac.models.shared_db import db
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

class Deployment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    username: Mapped[str] = mapped_column(String, nullable=True)
    operator: Mapped[str] = mapped_column(String, nullable=True)
    deployment_dir: Mapped[str] = mapped_column(String, nullable=True)
    estimated_deploy_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_deploy_location: Mapped[str] = mapped_column(String, nullable=True)
    wmo_id: Mapped[str] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.current_timestamp(), nullable=True)
    compliance_check_report: Mapped[str] = mapped_column(String, nullable=True)
    compliance_check_passed: Mapped[bool] = mapped_column(Boolean, default=None, nullable=True) # see if None works with this, it was the default for the mongonengine verison
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    need_compliance_check: Mapped[bool] = mapped_column(Boolean, default=False)
    glider_name: Mapped[str] = mapped_column(String, nullable=True)
    deployment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    archive_safe: Mapped[bool] = mapped_column(Boolean, default=True)
    checksum: Mapped[str] = mapped_column(String, nullable=True)
    attribution: Mapped[str] = mapped_column(String, nullable=True)
    delayed_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    latest_file: Mapped[str] = mapped_column(String, nullable=True)
    latest_file_mtime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    activate: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_file: Mapped[str] = mapped_column(String, nullable=True)

    def update_wmoid_file(self):
        # Keep the WMO file updated if it is edited via the web form
        wmo_id = ""
        if self.wmo_id is not None and self.wmo_id != "":
            wmo_id_file = os.path.join(self.full_path, "wmoid.txt")
            if os.path.exists(wmo_id_file):
                # Read the wmo_id from file
                with open(wmo_id_file, 'r') as f:
                    wmo_id = str(f.readline().strip())

            if wmo_id != self.wmo_id:
                # Write the new wmo_id to file if new
                with open(wmo_id_file, 'w') as f:
                    f.write(self.wmo_id)

    def get_latest_nc_file(self):
        '''
        Returns the lastest netCDF file found in the directory

        :param str root: Root of the directory to scan
        '''
        list_of_files = glob.glob('{}/*.nc'.format(self.full_path))
        if not list_of_files:  # Check for no files
            return None
        return max(list_of_files, key=os.path.getmtime)

    def set_compliance_check_flag(self):
        last_update = self.updated
        if last_update is not None and (datetime.now() - last_update).total_seconds() > 1800:
            app.logger.info("Deployment {} was last updated".format(self.deployment_dir))
        # eliminate force/always re-run?
        else:
            app.logger.info("Scheduling compliance check for completed "
                            "deployment {}".format(self.deployment_dir))
            self.need_compliance_check = True

    def on_complete(self):
        """
        sync calls here to trigger any completion tasks.

        - write or remove complete.txt
        - generate/update md5 files (removed on not-complete)
        - link/unlink via bindfs to archive dir
        - schedule checker report against ERDDAP endpoint # todo move this to other place
        """
        # Save a file called "completed.txt"
        completed_file = os.path.join(self.full_path, "completed.txt")
        if self.completed is True:
            with open(completed_file, 'w') as f:
                f.write(" ")
        else:
            if os.path.exists(completed_file):
                os.remove(completed_file)

        # generate md5s of all data files on completion
        if self.completed:
            for dirpath, _dirnames, filenames in os.walk(self.full_path):
                for f in filenames:
                    if (f in ["deployment.json", "wmoid.txt", "completed.txt"]
                            or f.endswith(".md5") or not f.endswith('.nc')):
                        continue

                    _full_file = os.path.join(dirpath, f)
            # todo move this to other place
            # # schedule the checker job to kick off the compliance checker email
            # # on the deployment when the deployment is completed
            # # on_complete might be a misleading function name -- this section
            # # can run any time there is a sync, so check if a checker run has already been executed
            # if getattr(self, "compliance_check_passed", None) is False:
            #     last_update = getattr(self, "updated", None)
            #     if last_update is not None and (datetime.now - last_update).total_seconds() > 1800:
            #         app.logger.info("Deployment {} was last updated".format(self.deployment_dir))
            #     # eliminate force/always re-run?
            #     else:
            #         app.logger.info("Scheduling compliance check for completed "
            #                         "deployment {}".format(self.deployment_dir))
            #         queue.enqueue(glider_deployment_check,
            #                       kwargs={"deployment_dir": self.deployment_dir},
            #                       job_timeout=800)
            self.set_compliance_check_flag()
        else:
            for dirpath, _dirnames, filenames in os.walk(self.full_path):
                for f in filenames:
                    if f.endswith(".md5"):
                        os.unlink(os.path.join(dirpath, f))

    def init_path(self):
        if not os.path.exists(self.full_path):
            try:
                os.makedirs(self.full_path)
            except OSError:
                pass

    def sync(self):
        if app.config.get('NODATA'):
            return
        if not os.path.exists(self.full_path):
            try:
                os.makedirs(self.full_path)
            except OSError:
                pass

        # trigger any completed tasks if necessary
        self.update_wmoid_file()
        self.on_complete()
        self.calculate_checksum()

        # Serialize Deployment model to disk
        json_file = os.path.join(self.full_path, "deployment.json")
        with open(json_file, 'w') as f:
            f.write(self.to_json())

    def calculate_checksum(self):
        '''
        Calculates a checksum for the deployment based on the MongoKit to_json()
        serialization and the modified time(s) of the dive file(s).
        '''
        md5 = hashlib.md5()
        # Now add the modified times for the dive files in the deployment directory
        # We dont MD5 every dive file here to save time
        for dirpath, _dirnames, filenames in os.walk(self.full_path):
            for f in filenames:
                # could simply do `not f.endswith(.nc)`
                if (f in ["deployment.json", "wmoid.txt", "completed.txt"]
                        or f.endswith(".md5") or not f.endswith('.nc')):
                    continue
                mtime = os.path.getmtime(os.path.join(dirpath, f))
                mtime = datetime.utcfromtimestamp(mtime)

                md5.update(mtime.isoformat().encode('utf-8'))
        self.checksum = md5.hexdigest()

    def save(self):
        from glider_dac.models import User
        if self.username is None or self.username == '':
            user = User.query.filter_by(id=self.user_id).first()
            self.username = user.username

        # Update the stats on the latest profile file
        modtime = None
        latest_file = self.get_latest_nc_file()
        if latest_file:  # if there are indeed files, get name and modtime
            modtime = datetime.fromtimestamp(os.path.getmtime(latest_file))
            latest_file = os.path.basename(latest_file)
        self.latest_file = latest_file
        self.latest_file_mtime = modtime
        if not self.hash:
            self.hash = Deployment.generate_unique_hash(self.username)

        self.sync()
        self.updated = datetime.utcnow()
        self.create_or_update()

    def create_or_update(self):
        if self.id is not None:
            # if it has id, this is a new deployment that hasn't been entered into the database yet
            # so we need to save it.  This is when you add "New deployment" while logged in -- files must
            # later be added
            if self.compliance_check_report:
                self.compliance_check_report = str(self.compliance_check_report) #unsure why this is done atm, it was in the old version
        else:
            db.session.add(self)

        db.session.commit()

    @classmethod
    def get_deployment_count_by_operator(cls):
        query = Deployment.query.with_entities(Deployment.operator, func.count().label("count")).group_by(Deployment.operator).all()
        return [{"_id":operator, "count":count} for operator, count in query]

    @property
    def erddap(self):
        args = {
            'host': app.config['PUBLIC_ERDDAP'],
            'user': slugify(self.username),
            'deployment': slugify(self.name)
        }
        erddap_url = "http://%(host)s/erddap/tabledap/%(deployment)s.html" % args
        return erddap_url

    def delete(self, signal_kwargs=None, **write_concern):
        if os.path.exists(self.full_path):
            rmtree(self.full_path)
        if os.path.exists(self.public_erddap_path):
            rmtree(self.public_erddap_path)
        db.session.delete(self)
        db.session.commit()

    @property
    def title(self):
        if self.operator is not None and self.operator != "":
            return self.operator
        else:
            return self.username

    @property
    def full_path(self):
        the_path = os.path.join(app.config.get('DATA_ROOT'), self.deployment_dir)
        if not os.path.exists(the_path):
            try:
                os.makedirs(the_path)
            except OSError:
                pass
        return the_path

    @property
    def public_erddap_path(self):
        return os.path.join(app.config.get('PUBLIC_DATA_ROOT'), self.deployment_dir)
