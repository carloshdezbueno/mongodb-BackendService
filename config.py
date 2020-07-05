import os
import logging

# author and license information
AUTHOR = 'Example Examplus Examplicus'
AUTHOR_EMAIL = 'example@example.ex'
LICENSE = 'see license.md file for details'

# log configuration
DEBUG = True
LOG_LEVEL = logging.DEBUG

# flask configuration
PORT = 8080
HOST = '0.0.0.0'  # bind to all interfaces
TITLE = 'flask-MongoDB-example'
VERSION = '1.0'
APP_NAME = 'flask-MongoDB-example'
DESCRIPTION = 'Example to use flask and MongoDB'

# SQLUtils configuration
MONGO_URI = 'mongodb+srv://arduinoWM:chernandezre@arduinosensors.yvbii.mongodb.net/test?authSource=admin&replicaSet=atlas-pdmd2o-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true'
MONGO_DB = 'datosSensores'
MONGO_COLLECTION = 'sensores'

# application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
