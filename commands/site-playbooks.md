---
description: Look up the site playbook for a URL or domain, list playbooks, add a new one, or lint the store
allowed-tools: Read, Bash, Write
argument-hint: [lookup <url|domain> | list | add --file <path> --matches a,b [--force] | lint]
---
Invoke the `site-playbooks` skill with this input: **$ARGUMENTS**

When args are empty, run `list` to show every stored playbook. For a live
browser task, run `lookup <url>` first and apply the playbook it prints.
