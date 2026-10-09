# Bug Report

## Bug ID: BUG-001
**Title:** Registration fails when username is shorter than 6 characters
**Related test case ID:** TC-REGISTER-002
**Module or endpoint:** POST /api/register
**Preconditions:** The target API is available.
**Steps to reproduce:**
1. Send a `POST /api/register` request.
2. Compare the response with the expected result.
**Test data:**
```json
{
  "username": "u0f2e",
  "password": "Valid0f2e82c29"
}
```
**Expected result:**
- HTTP 400
- Message: `Username length must be at least 6 characters`
**Actual result:**
- HTTP 200
- Message: `Registration_successful`
**Failure reason:** Actual result does not match expected result
**Severity:** Major
**Priority:** High
**Status:** Open
