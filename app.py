import bcrypt
from db import DB
from flask import Flask, request, flash, redirect, url_for



app = Flask(__name__)
db = DB("example.db")

def verifyPassword(storedPasswordHash, providedPassword):
    return bcrypt.checkpw(providedPassword.encode('utf-8'), storedPasswordHash)
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
    # Fetch user password from database
    records = db.select("SELECT Password FROM Account WHERE Username = ?", (username,))
    if len(records) == 0:
        return {'status': 404, 'message': 'User not found: The username you entered does not exist'}, 404
    
    storedPasswordHash = records[0][0]
    if verifyPassword(storedPasswordHash, password):
        return {'status': 200, 'message': 'Login successful'}, 200
    else:
        return {'status': 401, 'message': 'Unauthorized: Invalid username or password'}, 401



if __name__ == '__main__':
    app.run(port=65000)
