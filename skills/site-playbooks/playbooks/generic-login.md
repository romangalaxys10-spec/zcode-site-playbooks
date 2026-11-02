---
matches: [generic-login]
kind: pattern
source: community-contributed, verify before relying on it
---

# generic-login (pattern: any login wall)

Use when the task's first blocker is a login screen on a site that has no
dedicated playbook. Community-contributed, verify before relying on it.

## Quirks

- Login forms are the least standardized UI surface on the web: labels,
  placeholders, and control order differ per vendor. Never hard-code
  "#username / #password"; discover fields on the live page.
- Many SSO sites (Okta, Auth0, Azure AD) redirect after submit; the success
  signal is a URL change back into the app, not a button state.
- A session may exist already: test for auth state first (fetch a known
  page, look for a user menu or avatar) before assuming login is needed.
- Remember-me and "stay signed in" checkboxes off by default is common;
  leaving them checked changes the cookie lifetime the next run sees.
- Password managers and autofill can pre-fill fields in a headless-ish
  browser; read back the visible value before submitting.

## Login flow

1. Find the form: `form` containing an `input[type=password]`.
2. Fill username from `input[autocomplete="username"]` or
   `input[name*="user" i]` or the first text input in that form; fill
   password from the type=password input.
3. Submit with the form's primary button (`button[type=submit]` or the
   button with text matching the page language: "Sign in", "Log in", "Log in").
4. Detect outcome: success = URL left the login path; failure = inline
   error text near the form ("incorrect password", "captcha required").
5. If a challenge page appears (OTP, 2FA, captcha), stop and hand off.

## Anti-bot behavior

- Three consecutive failed submits on the same account usually unlocks a
  temporary lockout or a captcha escalation. After two failures, stop and
  report; do not brute retry.
- Rate-limited logins return "too many attempts" HTML that looks like the
  login page; read the alert region before the next submit.
- Some sites flag headless fingerprints before the form is even shown
  (a 403 or a JS challenge on the login URL itself). Then the fix is the
  browser context, not the form.

## Reliable selectors/strategy

- Discovered selectors beat memorized ones: locate password input, then
  climb to its form parent, then find username input and submit button
  within that form only.
- `autocomplete` attributes are the most stable cross-site contract.
- After submit, wait for either a redirect (URL change) or an error node
  appearing, up to ~10s. Do not sleep a fixed 3s.
- Screenshot the form state before and after submit; it is the fastest
  way to see what the page actually did.

## What to hand to the human

- Any 2FA step: SMS, authenticator, device approval, email link.
- Account lockout or "contact support" screens.
- Missing credentials: the agent must not guess or reuse passwords from
  other sites; ask the user for the account or a saved-credential path.
