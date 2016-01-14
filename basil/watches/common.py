import logging
import os

logging = logging.getLogger(__name__)


def verify_parameters():
    if not os.environ.get('DB_USER', None):
        logging.critical('DB_USER not set in environment')
        os.exit(1)
    if not os.environ.get('DB_PASS', None):
        logging.critical('DB_PASS not set in environment')
        os.exit(1)
    if not os.environ.get('DB_HOST', None):
        logging.critical('DB_HOST not set in environment')
        os.exit(1)
    if not os.environ.get('DB_NAME', None):
        logging.critical('DB_NAME not set in environment')
        os.exit(1)


def database_connector():
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    return 'mysql://%s:%s@%s/%s?charset=utf8' % (db_user, db_pass, db_host, db_name)

