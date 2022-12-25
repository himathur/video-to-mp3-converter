import os
import gridfs
import pika
import json
from flask import Flask, request, send_file
# from flask_pymongo import PyMongo
from pymongo import MongoClient
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)
# server.config["MONGO_URI"] = "mongodb://root:password@host.minikube.internal:27017/videos"
# mongo db connection
# mongo = PyMongo(server, uri="mongodb://root:password@host.minikube.internal:27017/videos")
# uri = "mongodb://root:password@host.minikube.internal:27017/videos"
video_client = MongoClient(host="host.minikube.internal:27017",
                           username="root", password="password", authSource="admin")
video_db = video_client["videos"]
fs_videos = gridfs.GridFS(video_db)

mp3_client = MongoClient(host="host.minikube.internal:27017",
                         username="root", password="password", authSource="admin")
mp3_db = mp3_client["mp3s"]
fs_mp3s = gridfs.GridFS(mp3_db)

# pika for rabbitmq connection
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host="rabbitmq", heartbeat=600, blocked_connection_timeout=300))
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
    if err:
        return err
    access = json.loads(access)
    # json object to python object
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            print(f"gateway Upload function called", flush=True)
            err = util.upload(f, fs_videos, channel, access)
            print(f"Error of Upload function in Util", flush=True)
            if err:
                return err
        return "Sucess!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["Get"])
def download():
    access, err = validate.token(request)
    if err:
        return err
    access = json.loads(access)
    if access["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400
        # fid exits
        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except:
            print(err)
            return f"internal server error while downloading", 500
    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
