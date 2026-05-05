---
name: release-operator
description: "Run a CLI/app release end-to-end: verify state, update changelog/version, test packaging, commit, tag, push, publish, and verify installs."
display_name: "Release Operator"
brand_color: "#059669"
local_only: true
group: "Dev Workflow"
usage: "/release-operator:run"
summary: "End-to-end release execution with post-release install verification"
default_prompt: "Run the release end-to-end. Verify tests and package contents, update changelog/version, commit/tag/push, publish, then verify install/update locally and on any named remote hosts."
---

# Release Operator

A release is not done when the commit is made. It is done when a fresh consumer can install/update and the remote host agrees.

## When to Use

- The user says release, deploy, publish, `cpd`, or "do that release"
- A packaged CLI/app needs version bump, changelog, tag, and verification
- A remote host such as `vesta` should validate the install/update path

## When NOT to Use

- Pure local prototype work with no publish surface
- The repo has its own release automation and the user only asked for a small code fix
- There are unreviewed failing tests that need debugging first

---

<process>

## Phase 1: Establish Release Facts

Read the repo instructions and existing release docs/scripts. Determine:

- current version and target version
- package manager / build tool
- release target: npm, GitHub release, app notarization, static deploy, etc.
- required changelog format
- whether install/update must be verified on a remote host

Run:

```bash
git status --short
git tag --list --sort=-version:refname | head
```

## Phase 2: Quality Gates

Run the repo's standard checks. For Node CLIs, default to:

```bash
npm run check
npm pack --dry-run
```

For packaged CLIs, inspect the dry-run tarball contents and confirm support scripts advertised by doctor/live checks are included.

## Phase 3: Version and Changelog

- Move changelog entries from Unreleased to the target version/date.
- Bump package metadata and lockfiles together.
- Keep changelog user-facing, not just commit-shaped.

## Phase 4: Commit, Tag, Push, Publish

Use the repo's release script if present. Otherwise:

```bash
git add <changed files>
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push
git push origin vX.Y.Z
```

Then publish using the configured channel. Do not invent a publish command; inspect docs/scripts first.

## Phase 5: Post-release Verification

Verify the published artifact, not just the local checkout:

```bash
<tool> --version
<tool> doctor --smoke
<tool> update
```

If a remote host was named:

```bash
ssh vesta '<tool> update; <tool> --version; <tool> doctor --smoke'
```

Classify any warnings. Release blockers are install failure, wrong version, missing packaged files, broken smoke test, or stale remote config pointing at the wrong binary.

## Phase 6: Report

Return concise evidence:

- version/tag published
- checks run
- package/publish verification
- local install/update result
- remote install/update result
- any follow-up issues filed

</process>

<interlocks>

- Use `remote-host-verifier` for local/remote command comparison.
- Use `status-copy-trust-audit` before release when CLI status text changed.
- Use `changelog-writer` when changelog wording needs user-facing translation.

</interlocks>
