import bcrypt
import re
from db import DB
from flask import Flask, request, flash, redirect, url_for



app = Flask(__name__)
db = DB("example.db")

def verifyPassword(storedPasswordHash, providedPassword):
    return bcrypt.checkpw(providedPassword.encode('utf-8'), storedPasswordHash)

def hashPassword(password):
    salt = bcrypt.gensalt() # Generate new salt
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashedPassword
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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # check password complexity
    if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#_])[A-Za-z\d@$!%*?&#_]{8,}$', password) is None:
        return {'status': 400, 'message': 'Password does not meet the complexity requirements. Password must be at least 8 characters long, and contain one lowercase, uppercase, digit and special character.'}, 400
    
    # check if username already exists
    records = db.select("SELECT Username FROM Account WHERE Username = ?", (username,))
    if len(records) != 0:
        return {'status': 409, 'message': 'Conflict: The username already exists. Please choose a different username.'}, 409

    # create account:
    db.insert("INSERT INTO Account (Username, Password) VALUES (?,?)", (username, hashPassword(password)))
    print("accoint created")
    return {'status': 201, 'message': 'Account created successfully.'}, 201

if __name__ == '__main__':
    app.run(port=65000)
