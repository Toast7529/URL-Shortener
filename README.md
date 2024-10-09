
---

# URL Shortener API Documentation

This API allows users to create, manage, and track shortened URLs. The API uses JWT (JSON Web Token) for authentication and provides several endpoints for URL creation, deletion, redirection, and information retrieval.

## Authentication
All requests, except `/login` and `/register`, require an Authorization header in the following format:
```
Authorization: Bearer <JWT token>
```

---

## Endpoints

### 1. **Register**

**POST** `/register`

Create a new account with a username and password.

- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- **Response:**
  - `201 Created`
  ```json
  {
    "status": 201,
    "message": "Account created successfully.",
    "token": "<JWT token>"
  }
  ```

  - `400 Bad Request`: Username or password doesn't meet the requirements.
  - `409 Conflict`: Username already exists.

---

### 2. **Login**

**POST** `/login`

Authenticate a user and get an access token.

- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "message": "Login successful",
    "token": "<JWT token>"
  }
  ```

  - `401 Unauthorized`: Invalid username or password.
  - `404 Not Found`: User not found.

---

### 3. **Create URL**

**POST** `/createURL`

Create a new shortened URL.

- **Request Body:**
  ```json
  {
    "url": "string"
  }
  ```

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "message": "URL successfully created.",
    "shortenUrl": "shortURL"
  }
  ```

  - `400 Bad Request`: Missing or invalid URL.
  - `409 Conflict`: The original URL is already shortened by the same user.

---

### 4. **Delete URL**

**POST** `/deleteURL`

Delete a shortened URL.

- **Query Parameters:**
  - `shortenUrl`: The shortened URL ID to delete.

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "message": "URL successfully deleted.",
    "shortenUrl": "shortURL"
  }
  ```

  - `400 Bad Request`: Missing `shortenUrl` parameter.
  - `404 Not Found`: URL does not exist.

---

### 5. **Get User URLs**

**GET** `/getURLs`

Retrieve all URLs shortened by the authenticated user.

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "urls": [
      {
        "originalURL": "https://example.com",
        "shortenURL": "shortURL"
      }
    ]
  }
  ```

  - `404 Not Found`: No URLs found for the user.

---

### 6. **Get URL Info**

**GET** `/getURLInfo`

Retrieve information about a specific shortened URL.

- **Query Parameters:**
  - `shortenUrl`: The shortened URL ID to get information for.

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "originalURL": "https://example.com",
    "clickCount": 42
  }
  ```

  - `400 Bad Request`: Missing `shortenUrl` parameter.
  - `404 Not Found`: URL not found.

---

### 7. **Update URL**

**PUT** `/updateURL`

Update the original URL for a given shortened URL.

- **Request Body:**
  ```json
  {
    "shortenUrl": "string",
    "url": "string"
  }
  ```

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "message": "URL successfully updated."
  }
  ```

  - `400 Bad Request`: Missing `shortenUrl` or invalid URL.
  - `404 Not Found`: URL not found or update failed.

---

### 8. **Redirect to Original URL (JSON)**

**GET** `/s/<shortenUrlID>`

Get the original URL associated with the shortened URL in JSON format and increment the click count.

- **Response:**
  - `200 OK`
  ```json
  {
    "status": 200,
    "url": "https://example.com"
  }
  ```

  - `404 Not Found`: Shortened URL not found.

---

### 9. **Redirect to Original URL**

**GET** `/r/<shortenUrlID>`

Redirect to the original URL associated with the shortened URL and increment the click count.

- **Response:**
  - **302 Found**: Redirects the user to the original URL.
  - `404 Not Found`: Shortened URL not found.

---

## Error Codes

- `200 OK`: The request was successful.
- `201 Created`: The resource was successfully created.
- `400 Bad Request`: The request is missing required parameters or contains invalid data.
- `401 Unauthorized`: Authentication is required or the token is invalid.
- `404 Not Found`: The requested resource could not be found.
- `409 Conflict`: The resource already exists.
  
---
# Database Schema

## Account Table
```SQL
CREATE TABLE Account (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## ShortenedURLs
```SQL
CREATE TABLE ShortenedURLs (
    URLID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    OriginalURL TEXT NOT NULL,
    ShortURL TEXT UNIQUE NOT NULL,
    ClickCount INTEGER DEFAULT 0,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Account(UserID)
);
```
---