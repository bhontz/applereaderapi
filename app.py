"""
    App entry point
"""
from flask import Flask, request
from applereader import AppleReader

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run()

