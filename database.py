import logging

from sqlalchemy import create_engine, func, Table
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text, Enum


logger = logging.getLogger(__name__)

Base = declarative_base()


class Database(object):

    def __init__(self, url):
        self.engine = create_engine(url)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def create_all(self):
        Base.metadata.create_all(self.engine)
        logger.info('Created databases from schema')

    def safe(self, command, *args, **kwargs):
        try:
            getattr(self.session, command)(*args, **kwargs)
        except (TypeError, AttributeError):
            pass
        except (InvalidRequestError, IntegrityError) as e:
            logger.error(e)
            self.session.rollback()
