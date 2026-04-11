# Launcher Template

Use this template when designing a per-instance launcher for isolated app testing.

## Launcher Requirements

A good launcher should:
- default to dry run
- show the exact binary it chose
- show the exact state root and defaults suite
- print the final launch command verbatim
- support `--live`
- support targeted kill by instance name
- prefer builds that actually contain the needed test-mode flags
- write logs to a deterministic per-instance path

## Example Shape

```bash
app-test-instance lane-a
app-test-instance lane-a --live
app-test-instance lane-a --fixture smoke-ready --live
app-test-instance lane-a --kill --live
```

## Recommended Inputs

- `instance`
- `--app`
- `--state-root`
- `--defaults-suite`
- `--fixture`
- `--foreground`
- `--kill`
- `--live`

## Recommended Output Summary

Print at least:
- instance name
- binary path
- state root
- defaults suite
- fixture profile
- log path
- exact command

## Example Launch Contract

```bash
/path/to/AppBinary \
  --ui-test-mode \
  --instance-id lane-a \
  --state-root ~/.tmp/myapp/lane-a \
  --defaults-suite com.example.MyAppTests.lane-a \
  --fixture smoke-ready
```

## Targeted Teardown

Do not kill all copies of the app.

Use an instance-specific match pattern such as:
- `--instance-id lane-a`
- a per-instance environment variable
- a per-instance pid file under the state root

## Evidence of a Good Launcher

A good launcher reduces:
- stale build mistakes
- wrong-suite mistakes
- wrong-root mistakes
- accidental normal-mode launches
- accidental mass-kill behavior
