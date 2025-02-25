import validators
import random
import string
import bcrypt
import re
from db import DB
from tokenManager import TokenManager
from flask import Flask, request, flash, redirect, url_for



app = Flask(__name__)
db = DB("example.db")
tokenManager = TokenManager("testKey")
def verifyPassword(storedPasswordHash, providedPassword):
    return bcrypt.checkpw(providedPassword.encode('utf-8'), storedPasswordHash)

def hashPassword(password):
    salt = bcrypt.gensalt() # Generate new salt
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashedPassword

def generateShortURL(length=6):
    chars = string.ascii_letters + string.digits
    shortUrl = ''.join(random.choice(chars) for i in range (length)) 
    return shortUrl

def getAccessToken():
    accessToken = request.headers.get('Authorization')
    if accessToken is None:
        return {'status': 401, 'message': 'Missing Authorization header.'}, 401
    if not accessToken.startswith('Bearer '):
        return {'status': 401, 'message': 'Authorization header must start with "Bearer".'}, 401

    try:
        token = accessToken.split(" ")[1]
    except IndexError:
        return {'status': 401, 'message': 'Invalid token format.'}, 401

    return token
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
    records = db.select("SELECT UserID, Password FROM Account WHERE Username = ?", (username,))
    if len(records) == 0:
        return {'status': 404, 'message': 'User not found: The username you entered does not exist'}, 404
    
    storedPasswordHash = records[0][1]
    if verifyPassword(storedPasswordHash, password):
        accessToken = tokenManager.generateAccessToken(records[0][0])
        return {'status': 200, 'message': 'Login successful', 'token': accessToken}, 200
    else:
        return {'status': 401, 'message': 'Unauthorized: Invalid username or password'}, 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # check username length
    if len(username) < 8:
        return {'status': 400, 'message': 'Username does not meet the length requirements. Username must be at least 8 characters long'}, 400
    # check password complexity
    if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#_])[A-Za-z\d@$!%*?&#_]{8,}$', password) is None:
        return {'status': 400, 'message': 'Password does not meet the complexity requirements. Password must be at least 8 characters long, and contain one lowercase, uppercase, digit and special character.'}, 400
    
    # check if username already exists
    records = db.select("SELECT Username FROM Account WHERE Username = ?", (username,))
    if len(records) != 0:
        return {'status': 409, 'message': 'Conflict: The username already exists. Please choose a different username.'}, 409

    # create account:
    db.insert("INSERT INTO Account (Username, Password) VALUES (?,?)", (username, hashPassword(password)))
    records = db.select("SELECT UserID FROM Account WHERE Username = ?", (username,))
    accessToken = tokenManager.generateAccessToken(records[0][0])
    return {'status': 201, 'message': 'Account created successfully.', 'token': accessToken}, 201

@app.route('/createURL', methods=['POST'])
def createURL():
    # check token
    accessToken = getAccessToken()
    if isinstance(accessToken, tuple):
        return accessToken
    print(accessToken)
    decodedToken = tokenManager.decodeAccessToken(accessToken)
    if isinstance(decodedToken, dict) and 'message' in decodedToken:
        return decodedToken, decodedToken['status']

    userID = decodedToken.get('userID')
    data = request.get_json()
    originalUrl = data.get("url")
    # check if user already has the same url in use
    records = db.select("SELECT ShortURL FROM ShortenedURLs WHERE UserID = ? AND OriginalURL = ?", (userID, originalUrl))
    if len(records) != 0:
        return {'status': 409, 'message': 'Conflict: The url is already in use by you. Please choose a different url.'}, 409

    if not originalUrl or not validators.url(originalUrl):
        return {'status': 400, 'message': 'Missing URL.'}, 400
    
    shortUrlID = generateShortURL()
    records = db.select("SELECT * FROM ShortenedURLs WHERE ShortURL = ?", (shortUrlID,))
    # check if shortUrl is already in db
    while len(records) != 0:
        shortUrlID = generateShortURL()
        records = db.select("SELECT * FROM ShortenedURLs WHERE ShortURL = ?", (shortUrlID,))
    db.insert("INSERT INTO ShortenedURLs (UserID,OriginalURL,ShortURL) VALUES(?,?,?)", (userID, originalUrl, shortUrlID))

    return {'status': 200, 'message': 'URL successfully created.', 'shortenUrl': shortUrlID}, 200

@app.route('/deleteURL', methods=['POST'])
def deleteURL():
    # check token
    accessToken = getAccessToken()
    if isinstance(accessToken, tuple):
        return accessToken
    print(accessToken)
    decodedToken = tokenManager.decodeAccessToken(accessToken)
    if isinstance(decodedToken, dict) and 'message' in decodedToken:
        return decodedToken, decodedToken['status']
    
    userID = decodedToken.get('userID')
    shortenUrlID = request.args.get("shortenUrl")
    
    if not shortenUrlID:
        return {'status': 400, 'message': 'Missing shortenUrl.'}, 400
    
    # Check if shortened URL exists for the user
    records = db.select("SELECT ShortURL FROM ShortenedURLs WHERE UserID = ? AND ShortURL = ?", (userID, shortenUrlID))
    if len(records) == 0:
        return {'status': 404, 'message': 'URL does not exist.'}, 404
    
    # Delete the shortened URL from the database
    db.delete("DELETE FROM ShortenedURLs WHERE UserID = ? AND ShortURL = ?", (userID, shortenUrlID))
    
    return {'status': 200, 'message': 'URL successfully deleted.', 'shortenUrl': shortenUrlID}, 200

@app.route('/getURLs', methods=['GET'])
def getURLS():
    # check token
    accessToken = getAccessToken()
    if isinstance(accessToken, tuple):
        return accessToken
    print(accessToken)
    decodedToken = tokenManager.decodeAccessToken(accessToken)
    if isinstance(decodedToken, dict) and 'message' in decodedToken:
        return decodedToken, decodedToken['status']

    userID = decodedToken.get('userID')
    # check if user already has the same url in use
    records = db.select("SELECT OriginalURL, ShortURL FROM ShortenedURLs WHERE UserID = ?", (userID,))
    if len(records) == 0:
        return {'status': 404, 'message': 'No URLs found for this user.'}, 404
    
    urls = [{'originalURL': row[0], 'shortenURL': row[1]} for row in records]
    return {'status': 200, 'urls': urls}, 200

@app.route('/getURLInfo', methods=['GET'])
def getURLInfo():
    # check token
    accessToken = getAccessToken()
    if isinstance(accessToken, tuple):
        return accessToken
    decodedToken = tokenManager.decodeAccessToken(accessToken)
    if isinstance(decodedToken, dict) and 'message' in decodedToken:
        return decodedToken, decodedToken['status']

    userID = decodedToken.get('userID')
    shortenUrlID = request.args.get("shortenUrl")
    # check if user already has the same url in use
    if shortenUrlID is None:
        return {'status': 400, 'message': 'Missing shortenUrl.'}, 400
    record = db.select("SELECT OriginalURL, ClickCount FROM ShortenedURLs WHERE UserID = ? AND ShortURL = ?", (userID, shortenUrlID))
    if len(record) == 0:
        return {'status': 404, 'message': 'URL not found.'}, 404
    
    return {'status': 200, 'originalURL': record[0][0], 'clickCount': record[0][1]}, 200

@app.route('/updateURL', methods=['PUT'])
def updateURL():
    # check token
    accessToken = getAccessToken()
    if isinstance(accessToken, tuple):
        return accessToken
    decodedToken = tokenManager.decodeAccessToken(accessToken)
    if isinstance(decodedToken, dict) and 'message' in decodedToken:
        return decodedToken, decodedToken['status']

    userID = decodedToken.get('userID')
    data = request.get_json()
    shortenURLID = data.get("shortenUrl")
    newURL = data.get("url")

    if not shortenURLID or not validators.url(newURL):
        return {'status': 400, 'message': 'Missing URL data.'}, 400

    records = db.update("UPDATE ShortenedURLs SET OriginalURL = ? WHERE UserID = ? AND ShortURL = ?", (newURL, userID, shortenURLID))
    if records == 0:    # check if records were found and updated
        return {'status': 404, 'message': 'URL not found or update failed.'}, 404
    return {'status': 200, 'message': 'URL successfully updated.'}, 200

@app.route('/s/<shortenUrlID>', methods=['GET'])
def redirectURL(shortenUrlID):
    record = db.select("SELECT OriginalURL, ClickCount FROM ShortenedURLs WHERE ShortURL = ?", (shortenUrlID,))
    
    if not record:
        return {'status': 404, 'message': 'Shortened URL not found.'}, 404
    
    originalURL = record[0][0]
    clickCount = record[0][1]
    
    db.update("UPDATE ShortenedURLs SET ClickCount = ? WHERE ShortURL = ?", (clickCount + 1, shortenUrlID))
    
    # return redirect url
    return {'status': 200, 'url': originalURL}, 200

@app.route('/r/<shortenUrlID>', methods=['GET'])
def redirectURL(shortenUrlID):
    record = db.select("SELECT OriginalURL, ClickCount FROM ShortenedURLs WHERE ShortURL = ?", (shortenUrlID,))
    
    if not record:
        return {'status': 404, 'message': 'Shortened URL not found.'}, 404
    
    originalURL = record[0][0]
    clickCount = record[0][1]
    
    # Increment the click count
    db.update("UPDATE ShortenedURLs SET ClickCount = ? WHERE ShortURL = ?", (clickCount + 1, shortenUrlID))
    
    # Redirect to the original URL
    return redirect(originalURL)
if __name__ == '__main__':
    app.run(port=65000)
