from flask import Flask
from flask_restful import Api,Resource,reqparse
import NSmodel
import NSSmodel
from flask_cors import CORS
from flask import jsonify
import os

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
BASE_DIR = os.path.dirname(__file__)
parser = reqparse.RequestParser()
parser.add_argument('parameters', type=str)
parser.add_argument('dataSet', type=str)
parser.add_argument('row', type=str)

class NSmodelAPI(Resource):
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
            # data = eval(args['data'])
            # tempBest,paras,x,y,y_real = NSmodel.runData(f"{BASE_DIR}/data/{dataSet}.xlsx","production",data)
            # jsonObj = {"rsquare":tempBest,"paras":paras,"x":list(x),"y":list(y),"y_real":list(y_real)}
            args = parser.parse_args()
            params = eval(args['parameters'])
            dataSet = eval(args['dataSet'])
            row = eval(args['row'])
            tempBest,paras,x,y,y_real = NSmodel.postOne(f"{BASE_DIR}/data/{dataSet}.xlsx",params,row)
            jsonObj = {"rsquare":tempBest,"paras":paras,"x":list(x),"y":list(y),"y_real":list(y_real)}
            return jsonify(jsonObj)
        except Exception:
            return jsonify({"error":"error"})
        
api.add_resource(NSmodelAPI, '/api/<dataSet>/<id>')

class NSSmodelAPI(Resource):
    def get(self,dataSet,id):
        try:
            if id != "-1":
                tau0, tau1, beta0, beta1, beta2, beta3, x, y_real, y, rs = NSSmodel.runOne(int(id),f"{BASE_DIR}/data/{dataSet}.xlsx")
                jsonObj = {"t0":tau0,"t1":tau1,"b0":beta0,"b1":beta1,"b2":beta2,'b3':beta3,'x':list(x),'y':list(y),'y_real':list(y_real),"rsquare":rs}
            else:
                jsonObj = {"error":"error"}
            return jsonify(jsonObj)
        except Exception:
            return jsonify({"error":"error"})

    def post(self,dataSet,id):
        try:
            args = parser.parse_args()
            params = eval(args['parameters'])
            dataSet = eval(args['dataSet'])
            row = eval(args['row'])
            tempBest,paras,x,y,y_real = NSSmodel.postOne(f"{BASE_DIR}/data/{dataSet}.xlsx",params,row)
            jsonObj = {"rsquare":tempBest,"paras":paras,"x":list(x),"y":list(y),"y_real":list(y_real)}
            return jsonify(jsonObj)
        except Exception:
            return jsonify({"error":"error"})

api.add_resource(NSSmodelAPI, '/api2/<dataSet>/<id>')

if __name__ == '__main__':
    app.run(debug=True)