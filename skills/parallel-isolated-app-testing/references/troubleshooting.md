# Troubleshooting Parallel Isolated App Testing

## Symptom: The app still lands in onboarding

Possible causes:
- fixture profile did not seed the true gating state
- seeded defaults went to the wrong suite/domain
- launcher used the wrong build
- app resets onboarding-related keys during launch

What to check:
- resolved defaults suite
- seeded keys actually present
- log lines during startup
- whether the launcher chose the intended binary

## Symptom: Two instances launch, but one steals focus or exits

Possible causes:
- duplicate-instance guard still active
- app activation logic assumes singleton behavior
- targeted launch contract is incomplete

What to check:
- duplicate-instance code path
- launch arguments on each process
- activation/focus logic in startup flow

## Symptom: Both lanes see each other's files or history

Meaning:
- the setup is not isolated enough

Likely causes:
- shared watched folder
- shared defaults suite
- shared app-support directory
- shared DB path

Action:
- stop deeper QA and fix isolation first

## Symptom: Processing always fails in smoke lanes

Possible causes:
- live dependency missing (API, Ollama, backend)
- fake-provider fixture does not exist yet
- auth state wrong for chosen provider

Action:
- separate isolation success from dependency success
- file a follow-up for fake-provider/stub mode if needed

## Symptom: UI automation cannot click anything

Possible causes:
- missing macOS Assistive Access
- blocked screen capture / automation permission
- agent/browser tooling not attached to the right process

Action:
- document the blocker explicitly
- avoid pretending deeper UI coverage happened
- continue with log-, file-, and state-based evidence where useful

## Symptom: The helper picks the wrong build

Possible causes:
- stale DerivedData build newer than the intended one
- helper only sorts by timestamp

Action:
- prefer binaries containing known test-mode markers
- allow explicit `--app` override
- print the chosen binary every time
