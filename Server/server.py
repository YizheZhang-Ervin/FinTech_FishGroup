from flask import Flask
from flask_restful import Api,Resource,reqparse
import NSmodel
from flask_cors import CORS
from flask import jsonify
import os

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
BASE_DIR = os.path.dirname(__file__)
parser = reqparse.RequestParser()
parser.add_argument('data', type=str)
parser.add_argument('dataSet', type=str)

class modelAPI(Resource):
    def get(self,dataSet,id):
        try:
            if id != "-1":
                tau0, beta0, beta1, beta2, x, y_real, y, rs = NSmodel.runOne(int(id),f"{BASE_DIR}/data/{dataSet}.xlsx")
                jsonObj = {"t0":tau0,"b0":beta0,"b1":beta1,"b2":beta2,'x':list(x),'y':list(y),'y_real':list(y_real),"rsquare":rs}
            else:
                tempBest,paras,x,y,y_real = NSmodel.runData(f"{BASE_DIR}/data/{dataSet}.xlsx","production")
                jsonObj = {"rsquare":tempBest,"paras":paras,"x":list(x),"y":list(y),"y_real":list(y_real)}

            return jsonify(jsonObj)
        except Exception:
            return jsonify({"error":"error"})
    
    def post(self,dataSet,id):
        try:
            args = parser.parse_args()
            data = eval(args['data'])
            dataSet = eval(args['dataSet'])
            tempBest,paras,x,y,y_real = NSmodel.runData(f"{BASE_DIR}/data/{dataSet}.xlsx","production",data)
            jsonObj = {"rsquare":tempBest,"paras":paras,"x":list(x),"y":list(y),"y_real":list(y_real)}
            return jsonify(jsonObj)
        except Exception:
            return jsonify({"error":"error"})

api.add_resource(modelAPI, '/api/<dataSet>/<id>')


if __name__ == '__main__':
    app.run(debug=True)