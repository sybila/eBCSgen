import sys

from flask import Flask, request
from flask import make_response

# this is hack, has to be resolved !!!
sys.path.append('../')
from Parsing.ParseBCSL import Parser

app = Flask(__name__)

@app.route("/")

@app.route("/ping", methods=['GET'])
def ping():
    if request.method == 'GET':
        response = make_response(str({"online": True}))
        response.headers['Content-Type'] = "application/json"
        # print(response.data)
        return response


@app.route('/bcsl_parse', methods=['POST'])
def bcsl_parse():
    if request.method == 'POST':
        start = request.form['start']
        expression = request.form['expression']

        parser = Parser(start)
        result = parser.syntax_check(expression)

        response = make_response(str({"success": result.success, "data": str(result.data)}))
        response.headers['Content-Type'] = "application/json"
        # print(response.data)
        return response

if __name__ == "__main__":
    app.run() # debug = True)
