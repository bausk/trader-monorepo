#!/usr/local/bin/python3
import json
import os
from os import path
from flask import Flask, jsonify
from flask_cors import cross_origin, CORS


app = Flask(__name__)
CORS(app)

@app.route("/")
def hello3():
    return "Hello world"

@app.route("/api/private2")
def hello4():
    return "Hello private world2"

if __name__ == '__main__':
    app.debug = False
    app.run(host="0.0.0.0", port=3000)
