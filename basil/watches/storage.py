import json
import logging

from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

logging = logging.getLogger(__name__)
Base = declarative_base()


class Monitoring(Base):
    __tablename__ = 'watches'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100))

    @staticmethod
    def find(session, prefix=None):
        query = session.query(Monitoring)
        if prefix:
            query = query.filter(Monitoring.name.like(prefix + '%'))

        return query.all()

    @staticmethod
    def delete(session, by_id):
        session.query(Monitoring).filter_by(id=by_id).delete()
        logging.info('deleting %s', by_id)

    @staticmethod
    def create(session, by_id, named):
        to_monitor = Monitoring(id=by_id, name=named)
        session.add(to_monitor)
        logging.info('creating %s %s', by_id, named)

    @staticmethod
    def get(session, by_id):
        return session.query(Monitoring).filter_by(id=by_id).first()

    def as_dict(self):
        return {'id': self.id, 'name': self.name.decode('utf-8', 'replace')}

    def is_clean(self):
        try:
            json.dumps({'name': self.name})
        except UnicodeDecodeError:
            logging.warning('UnicodeDecodeError decoding:: id=%s name=%s\n'
                            % (self.id, self.name))
            return False
        else:
            return True


class DBSessionFactory(object):
    def __init__(self, sessions):
        self.sessions = sessions

    def process_request(self, req, resp):
        logging.debug('Setting up session')
        req.context['session'] = self.sessions()

    def process_response(self, req, resp, resource):
        try:
            # TODO look up a better way to do this /if/
            resp_status = int(resp.status.split(' ', 1)[0])
            if resp_status in [201, 202, 204]:
                try:
                    logging.debug('Committing')
                    req.context['session'].commit()
                except Exception:
                    logging.debug('Rolling Back due to sql error')
                    raise
            elif resp_status >= 400:
                logging.debug('Rolling Back: error status %d', resp_status)
            else:
                logging.debug('Rolling Back: read-only operation')
        finally:
            self.sessions.remove()


def prepare_storage(connect_str):
    engine = create_engine(connect_str, pool_recycle=7200)
    return scoped_session(sessionmaker(bind=engine))


def migrate_db(connect_str):
    engine = create_engine(connect_str)
    Base.metadata.create_all(engine)
