# Skill: live-preview-dev (portable master)

**Capability:** Run a site locally and share a live preview URL.
**Category:** software-development
**Platforms:** linux
**Tags:** Preview, Frontend, Tunnel

## When to Use
Whenever you build or edit a website/app and need to (a) verify it renders and (b) give
the user a clickable link to interact with the real thing from any device. Combines a
self-check screenshot loop with a public tunnel URL.

## How to Run
Generic capabilities: `run a shell command`, `screenshot a page`, `read a file`,
`edit part of a file`. A tunnel binary (cloudflared quick tunnel, no account needed, or
ngrok) must be available; install it once if missing.

## Procedure
1. **Prepare the project.** Locate or scaffold it and install dependencies.
   _Done when:_ the install command exits 0.
2. **Start the dev server in the background on a known port, bound to `0.0.0.0`.**
   Binding to `0.0.0.0` (not `127.0.0.1`) is required so the tunnel can reach it.
   _Done when:_ the port is listening (a local request returns HTML).
3. **Self-check with a screenshot of the local URL.**
   _Done when:_ the screenshot shows rendered content, not a blank page or error stack.
4. **If blank or broken, debug.** Read server logs and the browser console, fix the root
   cause, restart, and re-screenshot.
   _Done when:_ the screenshot renders correctly.
5. **Expose a public URL via a tunnel** pointed at the dev port, run in the background
   (e.g. a cloudflared quick tunnel).
   _Done when:_ the tunnel prints a public `https://` URL that loads the site externally.
6. **Hand the public URL to the user** and keep both the server and tunnel processes alive.
   _Done when:_ the user-facing URL returns 200 from an external request.
7. **On every change:** apply the edit, let the server hot-reload, re-screenshot to
   confirm, and re-share the URL if the tunnel restarted.
   _Done when:_ the latest change is visible in the screenshot and at the public URL.

## Pitfalls
- Showing the user a URL before self-checking — a blank/broken build reaches them.
- Binding the server to `127.0.0.1`; the tunnel then gets connection-refused.
- Running server or tunnel in the foreground so they die when the step ends — always
  background them and confirm they stay up.
- Forgetting to re-screenshot after edits (you show stale state).
- Assuming hot-reload worked; verify with a fresh screenshot.

## Verification
The public URL loads the current build in an external browser, and the latest screenshot
matches what that URL serves.
