"""
    App entry point
"""
from flask import Flask, request
from flask_cors import CORS   # gets around Access-Control-Original errors from localhost app testing
from applereader import AppleReader

app = Flask(__name__)
CORS(app)
appClass = AppleReader()

# TODO: need book search call combining the google and lexile apis

@app.route('/username', methods=['GET'])
def getUserName():
    if request.method == 'GET':
        item = request.args.get('items', default=None, type=str)  # items is intended to be a comma delimited string

        return appClass.getUserName(item)

    return

@app.route('/firebase', methods=['GET'])
def getFirebaseKeys():
    if request.method == 'GET':
        child = request.args.get('child', default=None, type=str)
        username = request.args.get('username', default=None, type=str)

        return appClass.getFirebaseKeys(child, username)

    return

@app.route('/findbook', methods=['GET'])
def getBookDetail():
    if request.method == 'GET':
        typeparam = request.args.get('type', default=None, type=str)
        parameter = request.args.get('item', default=None, type=str)

        return appClass.getBookDetail(typeparam, parameter)

@app.route('/activities', methods=['GET'])
def getFireBaseActivities():
    if request.method == 'GET':
        username = request.args.get('username', default=None, type=str)

        return appClass.getFirebaseActivities(username)


if __name__ == '__main__':
    app.run()

