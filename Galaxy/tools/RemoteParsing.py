#!/usr/bin/python3

import sys, os
import json

from flask import Flask, request
from flask import make_response

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(os.path.split(sys.path[0])[0])[0])

from eBCSgen.Parsing.ParseBCSL import Parser

app = Flask(__name__)

@app.route("/")

@app.route("/BCSLparser/ping", methods=['GET'])
def ping():
    if request.method == 'GET':
        response = make_response(str({"online": True}))
        response.headers['Content-Type'] = "application/json"
        return response


@app.route('/BCSLparser/parse', methods=['POST'])
def parse():
    if request.method == 'POST':
        data = request.get_json()
        start = data['start']
        expression = data['expression']

        parser = Parser(start)
        result = parser.syntax_check(expression)

        response = {"success": result.success}

        if not result.success:
            response.update(result.data)
            response["expected"] = list(response["expected"])

        return json.dumps(response)

if __name__ == "__main__":
    app.run() #debug=True)
