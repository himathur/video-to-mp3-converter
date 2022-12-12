import os
import gridfs
import pika
import json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# mongo db connection
mongo = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
fs = gridfs.GridFS(mongo.db)

# pika for rabbitmq connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    print("reached login function")
    token, err = access.login(request)
    print(f"token: {token}")
    print(f" error: {err}")

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    access = json.loads(access)
    # json object to python object

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access)
            if err:
                return err
        return "Sucess!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["Get"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
