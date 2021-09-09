from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    db = SQLAlchemy(app)
    #CORS(app, resources={r"*/api/*" : {origins: '*'}})
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

    #@cross_origin
    @app.route('/')
    def hello_world():
        return jsonify({'message':'HELLO, WORLD!'})
    return app