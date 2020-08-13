from datetime import datetime
import json
import socket

from flask import Flask
from flask_cors import CORS
from flask_restplus import Api, Resource, reqparse
from werkzeug.exceptions import BadRequest, NotFound

from config import APP_NAME
from MongoDBUtils.MongoDBUtils import MongoDB
from ArduinoConnection import ArduinoConnection

# flask configuration
app = Flask(APP_NAME)
app.config.from_object('config')

api = Api(app, version=app.config['VERSION'],
          title=app.config['TITLE'], description=app.config['DESCRIPTION'])
mongodb_service = api.namespace('v1', description=app.config['DESCRIPTION'])

# flask anti CORS policy configuration
CORS(app)

# instance my SQLUtils wrapper
mongoDB = MongoDB(app.config['MONGO_URI'], app.config['MONGO_DB'])

# error handling
@api.errorhandler(BadRequest)
def handle_bad_request_exception(error):
    print(error)
    return {"message": str(error)}, 403


@api.errorhandler(NotFound)
def handle_not_found_exception(error):
    return {"message": str(error)}, 404


@api.errorhandler
def default_error_handler(error):
    return {"message": str(error)}, 500


@mongodb_service.route("/")
class CheckStatus(Resource):
    """check status"""

    def get(self):
        return {"status": "OK"}

# define endpoint args parser
argument_parser = reqparse.RequestParser()


@mongodb_service.route("/grabData")
@mongodb_service.doc(
    params={})
class GrabDataArduino(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = argument_parser

    @api.expect(argument_parser)
    def post(self):
        """ask the arduino for data and insert data in db"""
        
        codRespuesta = 200

        arduinoDao = ArduinoConnection.get_instance()

        userID, datos = arduinoDao.getDataArduino()

        print("Su UserID es: " + userID)

        ip = socket.gethostbyname(socket.gethostname())
        

        datosUsuario = [{key: datos.pop(key) for key in ["UserID", "ipAddress"]} for datos in mongoDB.findUserID("usuarios", userID, ip)]

        if len(datosUsuario)!=1:
            try:
                mongoDB.deleteUserID("usuarios", userID)
            except Exception:
                print("error")

            mongoDB.insert("usuarios", { "UserID": userID, "ipAddress": ip })


        if datos and self._validateJSON(datos):
            datos = json.loads(datos.decode("utf-8"))

            temperatura, humedad, luz, movimiento = datos["temperatura"], datos[
                "humedad"], datos["luz"], datos["movimiento"]
            status = self._insert_db(
                temperatura, humedad, luz, movimiento, userID)

        elif datos and datos.decode("utf-8") == "":
            status = "No se realizo medicion"
            codRespuesta = 502
        else:
            status = "Se produjo algun error desconocido"
            codRespuesta = 500

        return {
            "status": status,
            "data": datos or {}
        }, codRespuesta

    @classmethod
    def _insert_db(cls, temperatura, humedad, luz, movimiento, userID):
        document = {
            "UserID": userID,
            "timestamp": datetime.today(),
            "temperatura": temperatura,
            "humedad": humedad,
            "luz": luz,
            "movimiento": movimiento
        }
        mongoDB.insert(app.config['MONGO_COLLECTION'], document)
        return "OK"

    @classmethod
    def _validateJSON(cls, jsonData):
        try:
            json.loads(jsonData)
        except ValueError:
            return False
        return True


argument_parserGet = reqparse.RequestParser()
argument_parserGet.add_argument(
    'userID', required=True, type=str, location='json', help='missing userID parameter')


@mongodb_service.route("/getData")
@mongodb_service.doc(
    params={'userID': 'UserID to use the api'})
class SQLGet(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = argument_parserGet

    @api.expect(argument_parserGet)
    def get(self):
        """get data from db"""

        userID = self._get_args()

        data = list(mongoDB.select(app.config['MONGO_COLLECTION'], userID))

        datos = self._selectKeys(
            data, ["timestamp", "UserID", "temperatura", "humedad", "luz", "movimiento"])

        return {
            "status": "OK",
            "data": datos
        }

    def _get_args(self):
        args = self.parser.parse_args()

        userID = args['userID']

        return userID

    @classmethod
    def _selectKeys(cls, data, keys):

        return [{key: datos.pop(key) if key != "timestamp" else datos.pop(key).strftime("%m/%d/%Y, %H:%M:%S") for key in keys} for datos in data]


argument_parserSend = reqparse.RequestParser()
argument_parserSend.add_argument(
    'orden', required=True, type=str, location='json', help='missing order parameter')


@mongodb_service.route("/sendOrder")
@mongodb_service.doc(
    params={'userID': 'UserID to use the api'})
class SendOrder(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = argument_parserSend

    @api.expect(argument_parserSend)
    def post(self):
        """write data in arduino serial port"""
        orden = self._get_args()

        if self.esNumero(orden):
            intOrden = int(orden)
            if intOrden <= 1 or intOrden > 40:

                return {
                    "status": "Error, solo dispones de los pines del 2 al 40"
                }, 400

        arduinoDao = ArduinoConnection.get_instance()

        status = arduinoDao.sendDataArduino(orden)

        return {
            "status": status
        }

    def _get_args(self):
        args = self.parser.parse_args()
        orden = args['orden']

        return orden

    @classmethod
    def esNumero(cls, cadena):
        try:
            int(cadena)
            return True
        except ValueError:
            return False
