---
matches: [github.com]
kind: site
source: community-contributed, verify before relying on it
---

# github.com

Community-contributed, verify before relying on it. Selector strategies here
were written from public knowledge and change without notice when GitHub
ships new UI.

## Quirks

- GitHub pages are React apps: after navigation, wait for hydration before
  reading the DOM. A "finished" document is not a rendered page.
- `input[type=search]` on the search box is deprecated-adjacent; the search
  form posts to /search with `o=` (sort), `q=` (query), `type=` (repositorie
  s|issues|code). The new search UI reads the `q` param but rewrites it.
- Repository pages split content between server-rendered HTML (README, file
  list) and lazy-loaded fragments (issues list, tabs). Scrolling triggers
  fetches; absence of elements can mean "not loaded yet", not "not there".
- The mobile menu and "more actions" overflow menus keep controls offscreen
  on desktop at narrow widths: the button may exist in DOM but be hidden.
- URLs in the web app are canonical: /owner/repo, /owner/repo/issues,
  /owner/repo/pulls. Reading the URL bar is a more reliable state signal
  than reading headings after SPA navigation.
- Keyboard shortcut `/` focuses search when not typing; `t` opens issues on
  a repo home. Useful for avoiding hover-heavy navigation.

## Login flow

- /login renders the user login; /login/device (device flow) and /login/session
  handle token flows. Standard fields: `input.login_field_header[aria-label*="Username"]`
  or by placeholder "Username or email address", password field by
  `type=password` inside `#login`.
- Two-factor: after password submit, a /login/challenge route may appear with
  device codes or an SMS prompt. Agents should stop at 2FA and hand off.
- If `session` cookie is present, /login redirects to /:owner or /, so use
  that redirect as the logged-in signal rather than hunting for an avatar.

## Anti-bot behavior

- Rate limiting on unauthenticated requests is tight (60/hour API, ~5/page
  views per IP without session). Repeated identical navigation in short
  time triggers a 429 with a countdown page; wait, do not loop.
- GitHub serves a "Verify you are human" interstitial for suspicious patterns
  (headless UA, fast identical form submits). Slow down, use the real
  browser profile, and stop if it appears twice.
- Do not fire more than one form submit per second on the same page.
- The commit flow checks a hidden CSRF-style token in the form
  (`authenticity_token`); reusing stale forms after navigation will 404.

## Reliable selectors/strategy

- Prefer stable anchors over CSS classes: the "New repository" button label,
  `aria-label`s on icon buttons, `data-testid` attributes where present.
- File browser: `a[data-testid="drop-down-menu-content"]` region or just
  navigate by URL (/owner/repo/blob/main/path) and read rendered text.
- Issues/Pulls: filter by changing URL params (`?q=is%3Aopen`), not by
  clicking tab pills, then read `ul[class*="issues"]` rows.
- Copy text from rendered cards; GitHub's own links are stable and parseable
  from anchor `href` attributes even when the DOM churns.
- When the page is busy, wait on `document.querySelector('main')` having
  non-empty content plus a settled network state.

## What to hand to the human

- 2FA / device-code entry, "Verify you are human" interstitials, and any
  account-level prompt (password reset, email verification).
- Destructive repo actions: delete repo, force-push, transfer ownership.
- Payment, billing, and org seat changes.
- Anything whose result the user will be accountable for: PR merges,
  releases, closing issues on a team's behalf.
