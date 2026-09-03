---
name: api-integration
description: Connect, authenticate and test any external API.
version: 0.1.0
author: Melique, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [API, Auth, Integration]
---

## When to Use
Whenever wiring the app to any external service such as payments, LLMs, social, email, or
data. Follow this instead of re-deriving auth and testing each time. Never trust stale model
knowledge of an API; confirm the current contract from official docs first.

## How to Run
Use `web_search` and `web_extract` to read current docs, `terminal` to run smoke-test calls,
`read_file` to confirm env credentials, and `write_file` plus `patch` to wire the integration.

## Procedure
1. Read current docs: `web_search` then `web_extract` the official page to confirm base URL,
   auth method, scopes, and endpoints. _Done when:_ you have the doc URL and a written list of
   required credentials and scopes.
2. Resolve credentials from environment only; never hardcode secrets. Confirm keys exist as env
   vars. _Done when:_ keys resolve from env and no literal secret appears in code.
3. Smoke-test one minimal authenticated call with `terminal` (e.g. a me or list endpoint) before
   building more. _Done when:_ the response is 2xx with the expected shape.
4. Prove auth-failure handling: try a bad or missing key and confirm a clear handled 401 or 403,
   not a crash. _Done when:_ a known-bad key produces a clean explicit error.
5. Wire the call behind a thin function that parses and returns typed data using `write_file` or
   `patch`; never return the raw response. _Done when:_ the function returns parsed data.
6. Test end-to-end from the real entry point, not just the isolated function. _Done when:_ a real
   user action triggers a successful live call.
7. Record endpoints, scopes, rate limits, and gotchas for reuse. _Done when:_ notes are saved.

## Pitfalls
- Hardcoding API keys instead of reading from env.
- Skipping the single-call smoke test and debugging a whole feature instead.
- Testing only the happy path with no auth-failure or rate-limit handling.
- Trusting the model's memory of an API instead of reading current docs.
- Returning raw responses and leaking schema churn into the whole app.

## Verification
A real end-user action produces a correct live API response and every credential comes solely
from environment variables.
