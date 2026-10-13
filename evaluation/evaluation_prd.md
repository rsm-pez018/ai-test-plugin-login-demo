# AI-QA Defect Detection Evaluation PRD

The registration and login APIs must enforce the following rules:

1. Username is required when registering or logging in.
2. Password is required when registering or logging in.
3. Username must contain at least 6 characters when registering.
4. Password must contain at least 6 characters when registering.
5. A duplicate username must be rejected during registration.
6. A nonexistent username must be rejected during login.
7. An incorrect password must be rejected during login.
8. Valid registration and login must succeed.

For every rule, generate positive, negative, boundary, and state-dependent
tests where applicable. For the duplicate-username rule, register the same
unique username twice and verify the second request is rejected.
