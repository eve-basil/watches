import logging


logging.basicConfig(
    format='[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s]'
           ' %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S +0000', level=logging.DEBUG
    )
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
