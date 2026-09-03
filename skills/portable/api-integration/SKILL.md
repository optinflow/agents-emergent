# Skill: api-integration (portable master)

**Capability:** Connect, authenticate and test any external API.
**Category:** software-development
**Platforms:** any
**Tags:** API, Auth, Integration

## When to Use
Whenever wiring the app to any external service (payments, LLMs, social, email, data).
Follow this instead of re-deriving auth/testing each time. Never trust stale model
knowledge of an API — confirm the current contract from official docs first.

## How to Run
Generic capabilities: `search the web`, `extract a web page`, `run a shell command`,
`read a file`, `write a file`, `edit part of a file`.

## Procedure
1. **Read current docs.** Search the web and extract the official docs to confirm the
   base URL, auth method, required scopes, and the endpoints you need.
   _Done when:_ you have the doc URL and a written list of required credentials/scopes.
2. **Resolve credentials from environment only.** Confirm required keys exist as env
   vars; never hardcode secrets in source.
   _Done when:_ keys resolve from env and no literal secret appears in code.
3. **Smoke-test one minimal authenticated call** (e.g. a `/me` or list endpoint) before
   building anything larger.
   _Done when:_ the response is 2xx with the expected shape.
4. **Prove auth-failure handling.** Try a deliberately bad/missing key and confirm it
   surfaces a clear, handled error (401/403), not a crash.
   _Done when:_ a known-bad key produces a clean, explicit error.
5. **Wire the call behind a thin function** that parses and returns typed data — never
   return the raw response dump to the caller.
   _Done when:_ the function returns parsed, predictable data.
6. **Test end-to-end from the real entry point** (UI action or CLI command), not just the
   isolated function.
   _Done when:_ a real user action triggers a successful live call.
7. **Record what you learned** — endpoints used, scopes, rate limits, gotchas — to memory.
   _Done when:_ notes are saved for reuse.

## Pitfalls
- Hardcoding API keys instead of reading from env.
- Skipping the single-call smoke test and debugging a full feature instead.
- Testing only the happy path (no auth-failure or rate-limit handling).
- Trusting the model's memory of an API instead of reading current docs.
- Returning raw responses, leaking schema churn into the whole app.

## Verification
A real end-user action produces a correct live API response, and every credential comes
solely from environment variables.
