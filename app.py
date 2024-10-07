import bcrypt
from db import DB
from flask import Flask, request, flash, redirect, url_for



app = Flask(__name__)
db = DB("example.db")
# Login -> username, password = accessToken
# Register -> username, password = accessToken
# GetURLS -> accessToken = json of info
# RemoveURL -> accessToken, urlID = status 200
# getURLInfo -> accessToken, urlID = json of info

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # Check if username and password match account
    records = db.select("SELECT * FROM Account WHERE Username = ? AND Password = ?", (username, password))
    if len(records) != 0:   # username and password are correct
        return {'status': 200}
    # Check if user exists, but wrong password is used
    records = db.select("SELECT * FROM Account WHERE Username = ?", (username,))
    if len(records) != 0:
        return {'status': 401, 'message': 'Unauthorized: Invalid username or password'}
    # Return 404 if account not found
    return {'status': 404, 'message': 'User not found: The username you entered does not exist'}


if __name__ == '__main__':
    app.run(port=65000)
