import datetime

from flask import current_app
from main import db
from main.util.common_utils import paranoid
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import (
    CHAR,
    DECIMAL,
    DateTime,
    Float,
    Index,
    LargeBinary,
    String,
    TIMESTAMP,
    Text,
    text,
    asc,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT

from .base import Base


class EntryImages(Base):
    __tablename__ = "entry_images"
    __table_args__ = {'extend_existing': True}

    id = db.Column(INTEGER(11), primary_key=True)
    image_array = db.Column(LONGTEXT)
    confidence = db.Column(Float(asdecimal=True))

    @classmethod
    def get_entry_by_id(cls, id):
        return cls.query.filter_by(id=id).all()


    @classmethod
    def get_by_confidence(cls, confidence):
        return cls.query.filter(cls.confidence >= confidence).all()

  

class ClassificationResult(Base):
    __tablename__ = "classification_result"
    __table_args__ = {'extend_existing': True}


    id = db.Column(INTEGER(11), primary_key=True)
    id_mother_image = db.Column(INTEGER(11))
    box = db.Column(String(64), nullable=False, server_default=text("''"))
    confidence = db.Column(Float(asdecimal=True))

    Index("id_mother_image", "id_mother_image")

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).all()
    
    @classmethod
    def get_by_mother_id(cls, id_mother_image):
        return cls.query.filter_by(id_mother_image=id_mother_image).all()
    
    @classmethod
    def get_by_confidence(cls, confidence):
        return cls.query.filter(cls.confidence >= confidence).all()
   

