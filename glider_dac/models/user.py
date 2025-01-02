import os
import secrets
from glider_dac.backend_app import app
from datetime import datetime
from glider_util.bdb import UserDB

from glider_dac.models.shared_db import db
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from passlib.hash import sha512_crypt

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    api_key: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    organization: Mapped[str] = mapped_column(String, nullable=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.current_timestamp(), nullable=True)
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    @classmethod
    def _check_login(cls, username, password):
        ret = False
        user = User.query.filter_by(username=username).first()
        if user:
            ret = sha512_crypt.verify(password, user.password)
        return ret
    
    @classmethod
    def authenticate(cls, username, password):
        if cls._check_login(username, password):
            usr = User.query.filter_by(username=username).first()
            return usr
        return None
    
    @classmethod
    def update(cls, username, password):
        u = UserDB(app.config.get('USER_DB_FILE'))
        return u.set(username.encode(), password.encode())

    @property
    def data_root(self):
        data_root = app.config.get('DATA_ROOT')
        return os.path.join(data_root, self.username)

    def generate_api_key(self):
        api_key = secrets.token_urlsafe(16)
        while True:
            usr = User.query.filter_by(api_key=api_key).first()
            if usr is None:
                return api_key
    @classmethod
    def generate_password(cls, password):
        return sha512_crypt.hash(password)

    def save(self):
        api_key = self.generate_api_key()
        self.api_key = api_key
        self.password = User.generate_password(self.password)
        if not self.hash:
            self.hash = User.generate_unique_hash(self.username)
        if len(User.query.all()) == 0:
            self.is_admin = True
            self.is_approved = True

        db.session.add(self)
        db.session.commit()
        # on creation of user, ensure that a directory with username is present
        self.ensure_dir(self.username)

    def ensure_dir(self, dir_name):
        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root)

    @property
    def is_authenticated(self):
        return self.username is not None

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return not self.is_active

    def get_id(self):
        return str(self.id)

    @classmethod
    def get_deployment_count_by_user(cls):
        from glider_dac.models.deployment import Deployment
        query = db.session.query(Deployment.user_id, func.count().label("count")).group_by(Deployment.user_id).all()
        return [{"_id":user_id, "count":count} for user_id, count in query]
