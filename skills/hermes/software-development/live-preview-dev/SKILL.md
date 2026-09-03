---
name: live-preview-dev
description: Run a site locally and share a live preview URL.
version: 0.1.0
author: Melique, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Preview, Frontend, Tunnel]
---

## When to Use
Whenever you build or edit a website or app and need to verify it renders and give the user
a clickable link to interact with the real thing from any device. Combines a self-check
screenshot loop with a public tunnel URL.

## How to Run
Use `terminal` to install deps, start the dev server, and run the tunnel; `browser_exec`
plus `vision_analyze` to screenshot and read the rendered page; `read_file` and `patch` to
inspect and edit source. Install a tunnel binary (cloudflared quick tunnel needs no account,
or ngrok) with `terminal` if it is missing.

## Procedure
1. Prepare the project: locate or scaffold it and install dependencies with `terminal`.
   _Done when:_ the install command exits 0.
2. Start the dev server in the background on a known port bound to 0.0.0.0 via `terminal`.
   Binding to 0.0.0.0, not 127.0.0.1, lets the tunnel reach it. _Done when:_ a local request
   returns HTML.
3. Self-check by screenshotting the local URL with `browser_exec` and reading it with
   `vision_analyze`. _Done when:_ the screenshot shows rendered content, not blank or an error.
4. If blank or broken, read server logs and console via `terminal`, fix with `patch`, restart,
   and re-screenshot. _Done when:_ the screenshot renders correctly.
5. Expose a public URL by starting a tunnel to the dev port in the background with `terminal`.
   _Done when:_ the tunnel prints a public https URL that loads the site externally.
6. Hand the public URL to the user and keep both server and tunnel processes alive. _Done when:_
   the user-facing URL returns 200 from an external request.
7. On every change: apply the edit with `patch`, let the server hot-reload, re-screenshot with
   `browser_exec`, and re-share the URL if the tunnel restarted. _Done when:_ the latest change
   is visible in the screenshot and at the public URL.

## Pitfalls
- Sharing the URL before self-checking, so a blank or broken build reaches the user.
- Binding the server to 127.0.0.1, which gives the tunnel connection-refused.
- Running server or tunnel in the foreground so they die when the step ends; always background
  them and confirm they stay up.
- Forgetting to re-screenshot after edits and showing stale state.
- Assuming hot-reload worked without a fresh screenshot.

## Verification
The public URL loads the current build in an external browser and the latest screenshot matches
what that URL serves.
