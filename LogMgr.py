
import logging
import logging.handlers
#import main


LOGGER_NAME = 'xpebot'
LOG_NAME = 'restserver.log'
LOG_SIZE = 50 * 1024 * 1024 # 50MB
LOG_COUNT = 10

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)


log_handler = logging.handlers.RotatingFileHandler(LOG_NAME, maxBytes=LOG_SIZE, backupCount=LOG_COUNT)
log.addHandler(log_handler)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

log_handler.setFormatter(formatter)

