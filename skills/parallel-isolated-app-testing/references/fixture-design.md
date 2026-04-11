# Fixture Design for Parallel App Testing

Fixtures should create useful test states without introducing mystery meat.

## Good Fixture Properties

Each fixture should be:
- narrow in purpose
- deterministic
- documented
- easy to reset
- named for the user-visible state it creates

## Recommended Fixture Types

### smoke-ready
Use to:
- bypass onboarding
- point to isolated input roots
- suppress low-value prompts
- land in a generally healthy post-setup state

### misconfigured-auth
Use to:
- verify auth error messaging
- verify recovery instructions
- verify support-summary accuracy

### paused
Use to:
- verify paused UI and resume flows
- verify lane-specific pause state

### history-seeded
Use to:
- open History with realistic data
- verify filtering, rendering, and diagnostics summaries

### feedback-ready
Use to:
- exercise feedback and diagnostics flows without onboarding blockers
- verify export paths and support summaries

### fake-provider
Use to:
- verify happy-path processing without live APIs or local model servers
- create deterministic rename/history outcomes

## Document Every Fixture

For each fixture, document:
- defaults written
- files created
- credentials stubbed or omitted
- expected visible state after launch
- known non-goals

## Anti-Patterns

Avoid fixtures that:
- do too many unrelated things
- silently depend on global machine state
- require manual cleanup to work twice
- make success impossible to interpret
