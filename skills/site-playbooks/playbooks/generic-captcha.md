---
matches: [generic-captcha]
kind: pattern
source: community-contributed, verify before relying on it
---

# generic-captcha (pattern: any captcha wall)

Use when a task is blocked by reCAPTCHA, hCaptcha, Arkose (FunCaptcha), or
a custom "I am not a robot" widget, and the site has no dedicated playbook.
Community-contributed, verify before relying on it.

## Quirks

- A passing captcha is usually invisible: the widget just disappears and
  the form proceeds. There is no "success" button; wait and re-check the
  page state instead of looking for confirmation.
- Failed captchas reset silently after ~60s or re-serve a new challenge.
  Timing the retry wrong can count as a new failure against the IP.
- reCAPTCHA v2 sitekeys are embedded in a `<g-recaptcha>` element; read
  `data-sitekey` to know which tenant you are in (tenant reputation
  differs and so do failure rates).
- hCaptcha embeds an `iframe` whose source is `challenges.hcaptcha.com`
  or `js.hcaptcha.com`; the widget body is cross-origin, so you can only
  observe it, never read its inner DOM.
- Some "captchas" are invisible (reCAPTCHA v3) and score the session; a
  bad score surfaces later as a hard block, not as a puzzle at all.

## Login flow

N/A: the "flow" is block, detect, and hand off. Detect the widget type
first, then decide.

1. reCAPTCHA v2 checkbox: the widget is a 302x302 area with an internal
   iframe; the checkbox click point is top-left, roughly 28px in. Use a
   real human-quality click (or the browser's trusted-event path), not a
   synthetic JS click.
2. hCaptcha: same widget shape; the iframe is in the same area.
3. Arkose/FunCaptcha: image-puzzle grids that need a drag path. Almost
   always treat as human-only.
4. If the site offers an alternative (email link, phone code), prefer it;
   it is faster and less fragile than the widget.

## Anti-bot behavior

- Captcha presence is itself the anti-bot signal: repeated challenge
  failures escalate the block (temp IP bans, account flags). One or two
  attempts maximum, then stop.
- Do not load captcha-solving services into an agent loop; they violate
  most ToS and degrade fast.
- If the challenge appears on a page that previously did not have one,
  the trigger is likely the session or IP behavior, not the form. Wait
  several minutes and retry with normal pacing.
- Headless fingerprints correlate with harder challenges; a real browser
  profile with stable cookies lowers the rate.

## Reliable selectors/strategy

- Detect by marker: `g-recaptcha` class, `#hcaptcha` iframe,
  `iframe[src*="arkoselabs"]`. Detection is reliable; solving is not.
- After a trusted click, poll the parent page for the widget's removal
  (the div that held the checkbox is gone or now contains a "verifying"
  spinner), up to 30s.
- Take a screenshot at each state change for the handoff message.

## What to hand to the human

- Every image puzzle, audio challenge, and "verify you are a human"
  drag-and-drop.
- The reCAPTCHA checkbox itself: most harnesses cannot generate a trusted
  event that passes silently, so hand off with a screenshot and the
  current task context.
- Any site offering a "provisional access" or support-escalation option.
