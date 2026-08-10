# Login Test Execution Report

## Project

AI Testing Agent Demo - Login API


## Test Environment

Backend: Flask

Database: SQLite

API Testing Tool: Postman

API Endpoint:

POST /api/login




# TC_LOGIN_001
## Test Scenario

Login with valid username and password


## Test Data

```json
{
    "username": "abcdef",
    "password": "123456"
}
```

## Expected Result

Login should be successful.


## Actual Result

Login successful.


## Status

PASS


# TC_LOGIN_002
## Test Scenario

Login with incorrect password


## Test Data

```json
{
    "username": "abcdef",
    "password": "111111"
}
```

## Expected Result

Login should fail.

The system should return:

"Invalid username or password"


## Actual Result

Login failed.

The system returned:

"Invalid username or password"


## Status

PASS




# TC_LOGIN_003
## Test Scenario

Login with non-existing username


## Test Data

```json
{
    "username": "unknown",
    "password": "123456"
}
```

## Expected Result

Login should fail.

The system should return:

"Invalid username or password"


## Actual Result

Login failed.

The system returned:

"Invalid username or password"


## Status

PASS