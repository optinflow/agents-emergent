# Portable Skills Library

Your permanent, agent-agnostic capability library. Skills here are the thing that
**compounds** — they outlive any single agent, harness, or set of tool names.

## Why two copies of every skill?

Each skill exists in two forms:

- **`portable/<name>/SKILL.md`** — the *master*. Written in generic capability terms
  (e.g. "take a screenshot of the running dev server"), not tied to any agent's tool
  names. This is the version you own forever and plug into any future agent.
- **`hermes/<category>/<name>/SKILL.md`** — a *compiled copy* for the Hermes loader.
  Same procedure, but stamped with Hermes' required frontmatter and its tool names
  (`terminal`, `browser_exec`, `vision_analyze`, etc.). Drop it at
  `/config/.hermes/skills/<category>/<name>/SKILL.md`, validate, install via `skill_manage`.

When you adopt a new agent later, you copy the **portable master** and re-stamp it with
that agent's tool vocabulary. Zero rewrites of the actual knowledge.

## The three foundational skills

| Skill | What it gives the agent |
|-------|-------------------------|
| `self-verification` | Never reports "done" until it has run/seen/tested the result. The single biggest capability multiplier. |
| `live-preview-dev` | Runs a site locally, self-checks with a screenshot, and exposes a live shareable URL you can click. |
| `api-integration` | Connects, authenticates, and tests any external API on rails instead of re-deriving it each time. |

## Generic → tool mapping (adapter layer)

Portable masters use these generic capabilities. Map them to any agent's real tools:

| Generic capability | Hermes tool | Emergent / CLI equivalent |
|--------------------|-------------|---------------------------|
| run a shell command | `terminal` | bash / execute_bash |
| read a file | `read_file` | view_file / cat |
| write a file | `write_file` | create_file |
| edit part of a file | `patch` | search_replace |
| search files | `search_files` | grep / glob |
| search the web | `web_search` | web_search |
| extract a web page | `web_extract` | crawl / fetch |
| screenshot a page | `browser_exec` + `vision_analyze` | screenshot_tool |
| delegate a sub-task | `delegate_task` | sub-agent call |
| schedule a job | `cronjob` | cron / scheduler |
