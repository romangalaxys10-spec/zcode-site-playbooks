---
matches: [google.com, google.co.uk, google.co.in, google.de, bing.com, duckduckgo.com]
kind: site
source: community-contributed, verify before relying on it
---

# google-search (and the big generic search engines)

Community-contributed, verify before relying on it. Search engine markup
changes frequently; prefer URL and text reading over memorized element
positions.

## Quirks

- The results page is one of the most frequently re-flowed pieces of HTML
  on the web. Do not depend on row numbers or nth-child selectors; search
  by visible text and the `h3 > a` pattern.
- "People also ask" boxes, image carousels, and knowledge panels inflate
  the DOM between real results; a result list is not necessarily the
  first 10 links on the page.
- URL-encoding of the query matters: building `https://www.google.com/search?q=...`
  by hand and letting the page handle it is more stable than clicking the
  search button (which may hit the "I'm feeling lucky" flow on some UIs).
- Consent interstitials appear for EU/UK IPs on first visit without a
  cookie; the interstitial and the real page are two different DOMs.
- Google serves different HTML to different fingerprints. What your agent
  sees may be the "basic HTML version" or a JS-heavy one; read what is
  there, do not assume.

## Login flow

- No login required for search. A logged-in session adds local/ads
  personalization; a clean, no-cookie session gives the most neutral
  result set, which is usually what an agent wants.
- If a "Choose location" or consent screen appears, accept defaults and
  note that result ordering may be geo-biased.

## Anti-bot behavior

- Fast query loops from one IP trigger a `/sorry` CAPTCHA interstitial or
  a 429. Pacing: one query every 2 to 5 seconds, randomish, with
  navigation between them.
- The CAPTCHA here is the same class as the generic-captcha playbook:
  one retry, then hand off.
- DuckDuckGo and Bing are much more tolerant of scripted pacing when you
  just need a second opinion or a fallback when Google walls you.
- Do not parallelize tabs with the same search; it spikes the IP signal.

## Reliable selectors/strategy

- Result titles: `h3 a` links; result URLs render as visible text on the
  anchor or its parent card; read both the `href` and the text.
- Filter by URL pattern: `.search?q=term` plus `&num=` for result count;
  time filters via `&tbs=cdr:1,cd_min:...,cd_max:...` (read the docs page
  when you build these; the param names shift).
- Read snippets from the meta description block under the title; the
  first two results plus the snippet usually answer a factual question
  without clicking through.
- If the page shows "no results", try dropping to a shorter query; the
  engine truncates long queries differently across sessions.

## What to hand to the human

- CAPTCHA / `/sorry` interstitials.
- Account-level "sign in to continue" walls (rare for search, present on
  some federated search features).
- Anything the user will cite or act on: agents should mark which result
  they used, with URL and date, so the human can re-verify.
