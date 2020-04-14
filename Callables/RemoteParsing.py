#!/usr/bin/python3.6

import sys, os

from flask import Flask, request
from flask import make_response

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser

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
        start = request.form['start']
        expression = request.form['expression']

        parser = Parser(start)
        result = parser.syntax_check(expression)

        response = make_response(str({"success": result.success, "data": str(result.data)}))
        response.headers['Content-Type'] = "application/json"
        return response

if __name__ == "__main__":
    app.run() # debug = True)
