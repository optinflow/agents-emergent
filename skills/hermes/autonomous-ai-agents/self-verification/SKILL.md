---
name: self-verification
description: Verify your own work before reporting a task done.
version: 0.1.0
author: Melique, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Verification, Reliability, QA]
---

## When to Use
Use on every task that produces an observable result: a running service, a file, a built
page, an API response, or a deployed URL. This is default behavior, not optional. If you
cannot point to concrete evidence the result is correct, the task is not done.

## How to Run
Use `terminal` to run and inspect artifacts, `read_file` to read outputs back,
`browser_exec` plus `vision_analyze` to view rendered pages, and `web_search` to confirm
expected behavior when unsure.

## Procedure
1. Name the observable output: state exactly what a correct result looks like and how you
   will check it. _Done when:_ you have listed concrete, checkable acceptance criteria.
2. Do the task fully with no partial hand-off. _Done when:_ all intended changes are applied.
3. Run the artifact via `terminal` (start the service / execute the code). _Done when:_ the
   process is up or the command exits 0.
4. Capture real evidence: `terminal` to curl an endpoint, `read_file` to read a file back,
   `browser_exec` + `vision_analyze` to view a page. _Done when:_ you hold concrete evidence.
5. Compare to expected and mark each criterion pass or fail. _Done when:_ every criterion has
   a verdict.
6. If any fail, read logs, fix the root cause, and repeat from step 3. _Done when:_ zero
   failing criteria remain.
7. Report citing the actual evidence checked, not intent. _Done when:_ the report references
   the evidence.

## Pitfalls
- Claiming done from reading code without running it.
- Ignoring server or console logs when output looks off.
- Testing localhost when the real path is an external URL.
- Not re-testing after a fix, causing silent regressions.
- Confirming a service is configured instead of confirming it behaves correctly.

## Verification
An independent reviewer reproduces your evidence with `terminal` or `browser_exec` and gets
the same pass result.
