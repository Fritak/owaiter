from flask import Flask
from flask_restful import Api, Resource

from component.ImageTester import ImageTester
import socket


class Checker(Resource):
    def __init__(self, **kwargs):
        self.ImageTester = ImageTester(kwargs['config']['app']['OverwatchAppName'])

    def get(self):  # name
        isComp, isQp = self.ImageTester.analyze()
        result = {
            "isComp": isComp,
            "isQp": isQp
        }

        return result, 200


class Alive(Resource):
    def get(self):
        return {
                   "connected": True,
               }, 200


class ApiServer:
    def __init__(self, debug, config):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.debug = debug
        self.config = config

        # add resources
        self.api.add_resource(Checker, "/check", resource_class_kwargs={'config': self.config})
        self.api.add_resource(Alive, "/alive")
        # self.api.add_resource(User, "/check/<string:name>")

    def run(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
        except:
            print("Unable to get Hostname and IP")
            host_ip = "127.0.0.1"

        self.app.run(host=host_ip)
