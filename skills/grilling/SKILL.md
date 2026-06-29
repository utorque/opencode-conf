---
name: grilling
description: Interview the user relentlessly about a plan or feature design to reach shared understanding before building. Use when the user wants to stress-test a plan, align on a feature, or uses any 'grill' / 'grilling' / 'stress-test the plan' trigger phrases, or during the alignment phase of plan mode.
---

# Grilling

Interview the user relentlessly about every aspect of the plan or feature until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, explore the codebase instead — read code, check existing patterns, ADRs, and domain terminology, then propose an answer grounded in what you found.

Use existing `question` tool at your disposition.

## Goal of the phase

Reach a shared understanding of:

1. **The problem** being solved and who it serves (user-facing, not implementation-facing). Focus on the WHY, deeply understand the fundamental reasons for the feature to be able to properly design it. Ask as many questions as needed to ensure proper alignement.
2. **The solution shape** at the highest useful level (not layer-by-layer)
3. **The seams** where the feature will be tested (prefer existing seams, highest seam possible, ideally one)
4. **Risks & dependencies** that could derail implementation

Do not move on to writing a PRD until the user confirms alignment. Summarize the shared understanding back to the user in a few lines and get explicit confirmation before transitioning.
