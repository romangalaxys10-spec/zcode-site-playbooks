# Site Playbooks

Per-site usage-knowledge playbooks for browser-operating agents: quirks, login
flow, anti-bot behavior, and the selector strategy that actually works,
organized per domain or per generic pattern.

## Why

Every agent session on a real site re-discovers the same ground: where the
login button is, what triggers the captcha wall, which selectors survive a UI
refresh. The knowledge evaporates when the session ends. Site Playbooks keeps
it in one place, keyed to the URL, so the next agent run starts informed
instead of blind.

## How it works

| Step | What happens |
|------|--------------|
| Store | `skills/site-playbooks/playbooks/<domain-or-pattern>.md`, frontmatter `matches` globs + `kind` (site or pattern) |
| Before | `lookup <url>` prints the most specific matching playbook; the agent applies it |
| After | Agent discovered a quirk on a site? It offers to add a playbook; `add` validates frontmatter and refuses duplicates |
| Hygiene | `lint` re-parses every playbook in the store |

Seeded with four quality playbooks: `github.com`, `generic-login`,
`generic-captcha`, `google-search`. All seeds are marked community-contributed,
verify before relying on them.

## Install

1. Clone or download this repo to a folder.
2. In ZCode: Plugin Marketplace -> Add -> Add Plugin Marketplace, paste that folder path.
3. Install *Site Playbooks*.

Option B: copy the folder into your workspace `plugins/` directory.

## Try it

```
/site-playbooks lookup https://github.com/owner/repo
```

Expected: prints the github.com playbook with its Quirks, Login flow,
Anti-bot behavior, selector strategy, and human-handoff sections.

To register a new one you wrote:

```
python3 skills/site-playbooks/scripts/playbook_lookup.py add --file ./example.com.md --matches example.com,*.example.com
```

## Honest limits

- Matching is host-glob only; subdomain semantics are explicit (`*.github.com`
  does not match the apex `github.com`).
- Playbook content is community text, not verified fact. A playbook may be
  stale; when it contradicts the live page, trust the page and note it.
- `add` guards against name collisions, not against two playbooks whose
  globs overlap.

---

<p align="center">
  <a href="https://z.ai/subscribe?ic=R0K78RJKNW"><img alt="z.ai coding plans - 10% OFF coupon" src="https://img.shields.io/badge/z.ai%20coding%20plans-10%25%20OFF%20coupon-blueviolet" /></a>
  <a href="https://zcode.z.ai/invite/ALWM9JUA"><img alt="Try ZCode free" src="https://img.shields.io/badge/Try%20ZCode-free%20invite-0969da" /></a>
</p>

## License

MIT.
