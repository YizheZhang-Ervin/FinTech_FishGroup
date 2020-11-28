from flask import Flask
from flask_restful import Api,Resource
import NSmodel
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

class modelAPI(Resource):
    def get(self,id):
        avgDict,tindex,yields,spots = NSmodel.test(id)
        jsonObj = {"avgDict":avgDict,"tIndex":list(tindex),"yields":list(yields),"spots":list(spots)}
        return jsonify(jsonObj)

api.add_resource(modelAPI, '/api/<string:id>')


if __name__ == '__main__':
    app.run(debug=True)