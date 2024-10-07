import jwt
import datetime as datetime
class TokenManager():
    def __init__(self, key, algorithm='HS256'):
        self.__key = key
        self.__algorithm = algorithm
    
    def generateAccessToken(self, userID, expirationDelayMinutes=30):
        return jwt.encode({'userID': userID, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expirationDelayMinutes)}, self.__key, algorithm=self.__algorithm)

    def decodeAccessToken(self, token):
        try:
            data = jwt.decode(token, self.__key, algorithms=[self.__algorithm])
            return data
        except jwt.InvalidTokenError:
            return None
