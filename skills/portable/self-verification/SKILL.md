# Skill: self-verification (portable master)

**Capability:** Verify your own work before reporting a task done.
**Category:** autonomous-ai-agents
**Platforms:** any
**Tags:** Verification, Reliability, QA

## When to Use
Use on every task that produces an observable result: a running service, a file, a
built page, an API response, a deployed URL. This is a default behavior, not an
optional one. If you cannot point to concrete evidence that the result is correct,
the task is not done.

## How to Run
Use generic capabilities (map to your agent's tools via the library README):
`run a shell command`, `read a file`, `screenshot a page`, `search the web`.

## Procedure
1. **Name the observable output.** State exactly what a correct result looks like and
   how you will check it (endpoint returns 200, page renders X, file contains Y).
   _Done when:_ you can list concrete, checkable acceptance criteria.
2. **Do the task fully.** No partial hand-offs.
   _Done when:_ all intended changes are applied.
3. **Run the artifact.** Start the service / execute the code / open the file.
   _Done when:_ the process is up (port listening) or the command exits 0.
4. **Capture real evidence.** Curl the endpoint, screenshot the page, read the file
   back. Do not infer from code inspection.
   _Done when:_ you hold concrete evidence (status code, image, file contents, logs).
5. **Compare to expected.** Mark each acceptance criterion pass or fail.
   _Done when:_ every criterion has a pass/fail verdict.
6. **Fix and re-run.** If any criterion fails, read the error/logs, fix the root cause,
   and repeat from step 3.
   _Done when:_ zero failing criteria remain.
7. **Report with evidence.** State what you checked and the result.
   _Done when:_ the report cites the actual evidence, not intent.

## Pitfalls
- Claiming "done" from reading code without running it.
- Ignoring server/console logs when something looks off.
- Testing `localhost` when the real path is an external URL/ingress.
- Not re-testing after a fix (silent regressions).
- Verifying a service is *configured* (process running) instead of *behaving* (correct output).

## Verification
An independent reviewer can reproduce your evidence and get the same pass result.
