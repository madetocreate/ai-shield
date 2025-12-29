# Action Engine V2 (Frontend)

## What this is
A single, consistent execution path for all “AI actions” in the product UI.

**Pattern**
Action Tile → Preview → Apply → Audit

Chat may trigger an action, but the action result is never “stored in chat”.
The right drawer (Context | Actions | History) and the module result tabs are the home for outputs.

## Why V2
We want the system to stay safe, predictable, and scalable:
- No accidental auto-sends
- No duplicated actions on double-click
- Clear permissions and approvals
- Async-friendly for long-running actions (docs, long threads)
- Measurable and debuggable (observability)
- Output is bounded (no giant LLM walls of text)

## V2 Additions (must-have)

### 1) Action Policy / Permissions
Every action must declare:
- `riskLevel`: low | medium | high
- `requiresApproval`: boolean (UI gate)
- `permissions`: roles allowed (e.g. owner/admin/member)
- `dataAccess`: which context fields are allowed (whitelist)

**Rule:** if an action is not explicitly allowed, it is treated as disallowed.

### 2) Idempotency + Undo
- Every apply gets an `idempotencyKey` (derived from actionId + targetRef + contextHash + optionHash).
- If the user triggers the same apply twice, the second apply is a no-op.
- For supported actions we provide Undo:
  - tag add → tag remove
  - tasks created → tasks remove
  - memory entry created → memory entry remove
  - draft overwritten → restore previous draft
Undo is a small safety belt and reduces fear of “clicking AI”.

### 3) Async Job Mode
Some actions can take time (large docs, long threads).
The engine must support:
- `run()` returning a job object (jobId + status)
- UI can render: queued → running → completed → failed
- Preview appears when completed
For now: stub with setTimeout to simulate async.

### 4) Caching / Reuse
If the same action is run with the same context+options:
- reuse the previous result for a short TTL
- prevents repeated costs later
- improves UX (snappy)
Caching should be modular so it can later move server-side.

### 5) Observability (Audit that is actually useful)
Every run/apply should log:
- actionId, module, targetRef
- status: success/failed/canceled
- durationMs
- jobId / idempotencyKey
- safeErrorMessage (never secrets)
This is needed for debugging and for trust.

### 6) Output Limits (hard bounds)
Every action declares strict limits, e.g.:
- summary: max 5 bullets, max 600 chars
- draft: max 900 chars
- tasks: max 6 items
- extraction: max 12 fields
Normalizer enforces limits before preview.

## Chat Integration (Intent trigger)
Chat is a steering wheel, not a storage container.
- Chat (or quick actions) can call: `dispatchAction(actionId, targetRef)`
- Engine runs action and opens the right drawer preview for the current module.
- Chat may show a tiny “Action started” toast, but not the full output.

## Non-goals
- No real LLM calls in frontend
- No automatic sending
- No heavy CRM features
- No redesign

## Where to plug real LLM later
Replace `src/lib/actions/adapters/stubLLM.ts` with a server-side adapter that preserves the same output shapes and validation boundaries. The runner should keep caching, policy, and audit unchanged while swapping the adapter implementation.

