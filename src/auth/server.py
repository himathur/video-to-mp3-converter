import jwt
import datetime
import os
from flask import Flask, request
# from flask_mysqldb import MySQL

import mysql.connector
from mysql.connector import errorcode

# variables
server = Flask(__name__)
# mysql = MySQL(server)

# config
config = {
    'user': os.environ.get("MYSQL_USER"),
    'password': os.environ.get("MYSQL_PASSWORD"),
    'host': os.environ.get("MYSQL_HOST"),
    'database': os.environ.get("MYSQL_DB"),
    'port': os.environ.get("MYSQL_PORT"),
    'raise_on_warnings': True
}


@server.route("/login", methods=["POST"])
def login():
    # get basic creds from authorization header : auth.username -> email / auth.password
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    try:        
        cnx = mysql.connector.connect(**config)
        print(cnx, flush=True)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    cur = cnx.cursor()
    print(cur)

    cur.execute("SELECT email, password FROM user WHERE email=%s",
                (auth.username,))
    result = cur.fetchall()
    print(f"printing {result}", flush=True)
    for x in result:
        print(x, flush=True)
    if len(result) > 0:
        email = result[0][0]
        password = result[0][1]
        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)

    else:
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    print(encoded_jwt)
    # Authorization:Bearer <token>

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]  # this will return the token

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403
    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(port=5000, host="0.0.0.0", debug=True)
