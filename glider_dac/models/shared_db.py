from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase
import json
import datetime
import hashlib
import random

class Base(DeclarativeBase):
    def to_json(self, ignore_fields=[]):
        ret = {}
        for attr in inspect(self).mapper.column_attrs:
            attr_val = getattr(self, attr.data_field_name)
            if attr.data_field_name not in ignore_fields:
                if type(attr_val) is datetime.datetime:
                    ret[attr.data_field_name] = int(attr_val.timestamp() * 1000) #epoch time to miliseconds
                elif type(attr_val) is str and len(attr_val) > 0 and attr_val[0] == "{" and attr_val[-1] == "}":
                    ret[attr.data_field_name] = json.loads(attr_val)
                else:
                    ret[attr.data_field_name] = attr_val
        return json.dumps(ret, default=str) #need to change default, it's just because of datetime

    @classmethod
    def generate_unique_hash(cls, value_to_hash):
        byte_hash = value_to_hash.encode()
        hash = hashlib.sha256(byte_hash).hexdigest()
        while cls.query.filter_by(hash=hash).first() is not None:
            value_to_hash += str(random.randint(0,9))
            byte_hash = value_to_hash.encode()
            hash = hashlib.sha256(byte_hash).hexdigest()
        return hash
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        


db = SQLAlchemy(model_class=Base)

