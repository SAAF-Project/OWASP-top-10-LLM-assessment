# LLM10 — Unbounded Consumption

## Description
Unbounded Consumption occurs when an LLM application allows unrestricted resource use — token consumption, API calls, compute, or storage — leading to denial-of-service, runaway costs, or degraded availability for other users.

## Risk
- Runaway API costs from unconstrained batch processing or recursive agent loops
- Denial of service: large inputs exhaust token budgets, starving other requests
- Infinite loops in agentic pipelines with no termination condition
- Exfiltration via timing side-channels or resource exhaustion patterns

## Key Assessment Questions
1. Are there per-request token limits enforced at the application layer?
2. Is there a maximum recursion depth or loop iteration limit for agentic workflows?
3. Are total API costs monitored and alerted on anomalies?
4. Is input size validated and capped before sending to the model?
5. Are there rate limits per user, session, or workflow instance?

## Mitigations
- Enforce max_tokens limits on all API calls
- Set hard limits on agent loop iterations and recursion depth
- Validate and truncate inputs before sending to the model
- Implement cost monitoring and budget alerts
- Apply per-user and per-session rate limiting
