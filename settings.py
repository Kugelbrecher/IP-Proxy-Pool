import logging

# score of proxy ip
MAX_SCORE = 50

# log settings
LOG_LEVEL = logging.INFO
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
LOG_FILENAME = 'log.log'

# MongoDB
# if cloud atlas:
# MONGO_URL = "mongodb+srv://<username>:<password>@cluster0.bm07zwz.mongodb.net/?retryWrites=true&w=majority"
# if local:
MONGO_URL = "mongodb://127.0.0.1:27017"