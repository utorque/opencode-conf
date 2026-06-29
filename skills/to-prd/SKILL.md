---
name: to-prd
description: Synthesize the current conversation and codebase understanding into a PRD file. Use when the plan-mode alignment (grilling) phase is complete and the user wants to capture a feature as a Product Requirements Document. Writes the PRD to .opencode/plans/NNN_PRD_<clear_name>.md.
---

# To PRD

Take the current conversation context and codebase understanding and produce a PRD. Do NOT interview the user — just synthesize what you already know. (Alignment was done in the grilling phase.)

## Where PRDs live

- PRD files live in `.opencode/plans/`
- File name: `NNN_PRD_<clear_name>.md`
- `NNN` is the next zero-padded sequence number. Scan `.opencode/plans/` for existing `NNN_PRD_*.md` files (do not scan `archive/`) and pick the next free number. Start at `000` if none exist.
- `<clear_name>` is a short kebab-case slug describing the feature — readable and stable across the issue phase. e.g. `014_PRD_user-profile-export.md`
- When a PRD is Done or Cancelled, move its file to `.opencode/plans/archive/`
- No triage labels, no external issue tracker — the local file IS the artifact

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better — the ideal number is one.

   Check with the user that these seams match their expectations.

3. Pick the next `NNN` number and write the PRD file to `.opencode/plans/NNN_PRD_<clear_name>.md` using the template below.

<prd-template>

# PRD: <feature name>

- **ID**: NNN
- **Status**: Draft
- **File**: `NNN_PRD_<clear_name>.md`

## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each in the format:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- The seams chosen in process step 2
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>

## After writing

- Set `Status` to `Draft` while writing, then `Aligned` once the user signs off on the PRD. Sign-off may be explicit ("approved", "LGTM") or **implicit** — the user directing the next phase ("cut issues", "to-issues", "GO", "launch the subagents") counts as approval. Flip `Draft → Aligned` at the moment you hand off to the next phase; never leave a PRD at `Draft` once its issues are being cut.
- The PRD is the source of truth for the downstream `to-issues` phase.

## Lifecycle end (Aligned → Done)

- A PRD moves `Aligned → Done` when **every** non-archived issue under its parent reference has moved to `DONE` (or `CANCELLED`) and been moved to `.opencode/plans/issues/archive/`. Scan `issues/` (excluding `archive/`) for any remaining sibling of this PRD; if none, the PRD is complete.
- At that moment, the agent performing the last close-out flips `Status: Aligned → Done` and moves the PRD file to `.opencode/plans/archive/`.
- `Cancelled` supersedes any other state.
- If the implementing agent is one of several launched in parallel, the agent that launched them owns close-out (see AGENTS.md "Planning artifacts"); individual subagents only flip their own issue's `Status` and archive their own issue file.
