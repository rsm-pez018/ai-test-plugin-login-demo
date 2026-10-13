# Bug Report

## Bug ID

BUG_REGISTER_001


## Bug Title

Username length validation is missing in registration API


## Module

Register API


## Severity

Medium


## Priority

Medium


## Environment

Local Development Environment

Backend: Flask

Database: SQLite

API Endpoint: POST /api/register


## Description

According to the product requirement, the username length must be greater than or equal to 6 characters.

However, the current registration API does not validate the username length.

When a user enters a username with less than 6 characters, the system still allows the registration request to succeed.


## Preconditions

1. The Flask backend service is running.

2. The registration API is available.

3. The username has not been registered before.


## Steps to Reproduce

1. Send a POST request to `/api/register`.

2. Enter a username with less than 6 characters.

3. Enter a valid password.

4. Submit the registration request.


## Test Data

Request:

```json
{
    "username": "abc",
    "password": "123456"
}
```


## Expected Result

The registration request should fail.

The system should display:

"Username length must be at least 6 characters."


## Actual Result

The registration request succeeds.

The system creates the user account even though the username length is less than 6 characters.


## Difference Analysis

Expected behavior:

Username length less than 6 characters should be rejected.


Actual behavior:

Username length less than 6 characters is accepted and registration succeeds.


The actual implementation does not match the product requirement.


## Impact

Users can create accounts with invalid usernames.

This may lead to inconsistent user data and violates the registration requirements.


## Root Cause

The backend registration API does not implement username length validation.

The username length checking logic is missing.


## Suggested Fix

Add username length validation before creating a new user.

Example:

- Check whether the username length is at least 6 characters.
- Return an error response if the username length is less than 6 characters.
- Only allow registration when all validation rules are satisfied.


## Status

Open


## Attachment

API Request:

POST /api/register


Request Body:

```json
{
    "username": "abc",
    "password": "123456"
}
```


Actual Response:

```json
{
    "message": "Registration successful"
}
```