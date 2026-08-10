# Login Test Cases

## Project

AI Testing Agent Demo - Login API


## Module

Login


## API Endpoint

POST /api/login




# TC_LOGIN_001
## Title

Login with valid username and password


## Description

Verify that users can login successfully with correct credentials.


## Preconditions

A user account has been registered.


## Test Data

```json
{
    "username": "abcdef",
    "password": "123456"
}
```


## Steps

1. Send POST request to `/api/login`.

2. Enter valid username and password.

3. Submit the request.


## Expected Result

Login should be successful.


## Priority

High



# TC_LOGIN_002
## Title

Login with incorrect password


## Description

Verify that login fails when password is incorrect.


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


## Priority

High



# TC_LOGIN_003
## Title

Login with non-existing username


## Description

Verify that login fails when username does not exist.


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


## Priority

Medium