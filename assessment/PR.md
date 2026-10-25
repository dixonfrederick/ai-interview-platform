Recruiters could see a skill gap without its required level because the API emitted `expected_level` while the frontend read `required_level`. The review flow also lost reports on refresh failure, omitted rating provenance, and allowed portfolio/override lookups outside the authenticated tenant.

This change delivers one complete portfolio-to-vacancy review slice: deterministic comparisons with human-review provenance, explicit unassessed requirements, source fingerprints, persisted processing/retry states, tenant ownership checks, and consistent PDF/JSON exports. The UI supports evidence inspection, follow-up filtering, stale/failed snapshots, keyboard use, and narrow screens. Portfolio response validation prevents invented L1 ratings and preserves human overrides during regeneration.

The comparison deliberately replaces unsupported AI culture/hiring narratives with an evidence-based summary. Existing live interview behavior is outside this change.

Artifacts: [single PDF report](https://github.com/dixonfrederick/ai-interview-platform/blob/feat/reliable-assessment-review/assessment/submission.pdf), [3:30 captioned walkthrough](https://github.com/dixonfrederick/ai-interview-platform/releases/download/case-study-review-v1/review-walkthrough.mp4), and [runbook and defense notes](https://github.com/dixonfrederick/ai-interview-platform/tree/feat/reliable-assessment-review/assessment).

Validation: 61 backend examples, 11 frontend tests, 4 browser regression tests, a recorded real browser workflow, mobile accessibility, production build, and migration down/up with existing rows. Seeded fault proof is available on the fork's `proof/seeded-fitgap-fault` branch: 28 of 35 comparison examples failed before the deliberate fault was reverted. CI includes eager loading and all review checks. Test assertions were not weakened.

See `assessment/01-discovery-and-plan.md`, `assessment/02-product-context.md`, and `assessment/RUNBOOK.md` for acceptance criteria, product reasoning, trade-offs, setup, and deployment/rollback limitations. No live Gemini interview, production data, or measured hiring-quality improvement is claimed.
