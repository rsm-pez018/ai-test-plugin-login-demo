# Test Cases

## Project

AI Testing Agent Demo - Register API


## Module

Register


# TC_REGISTER_001

## Title

Register with valid username and password


## Description

Verify that users can successfully register with valid information.


## Test Data

```json
{
    "username": "abcdef",
    "password": "123456"
}
```


## Steps

1. Send POST request to `/api/register`.

2. Provide valid username and password.

3. Submit the request.


## Expected Result

Registration should be successful.


## Priority

High


# TC_REGISTER_002

## Title

Register with empty username


## Description

Verify that registration fails when username is empty.


## Test Data

```json
{
    "username": "",
    "password": "123456"
}
```


## Steps

1. Send POST request to `/api/register`.

2. Leave username empty.

3. Submit the request.


## Expected Result

Registration should fail.

The system should return:

"Username is required"


## Priority

High


# TC_REGISTER_003

## Title

Register with short password


## Description

Verify that registration fails when password length is less than 6 characters.


## Test Data

```json
{
    "username": "abcdef",
    "password": "123"
}
```


## Steps

1. Send POST request to `/api/register`.

2. Enter password with less than 6 characters.

3. Submit the request.


## Expected Result

Registration should fail.

The system should return:

"Password length must be at least 6 characters"


## Priority

Medium


# TC_REGISTER_004

## Title

Register with username length less than 6 characters


## Description

Verify that the system rejects usernames shorter than 6 characters.


## Test Data

```json
{
    "username": "abc",
    "password": "123456"
}
```


## Steps

1. Send POST request to `/api/register`.

2. Enter username with less than 6 characters.

3. Submit the request.


## Expected Result

Registration should fail.

The system should return:

"Username length must be at least 6 characters"


## Priority

High


## Status

Fail (Related Bug: BUG_REGISTER_001)