# AI verification record

AI assistance was used for repository analysis, planning, code, test scaffolding, documentation, and artifact preparation. Generated output was checked through source inspection, regression tests, real browser use, dependency auditing, and CI. No other candidate's PR or implementation was used.

## A generated dependency choice was unsafe

The initial test-harness command selected Vitest 3.2.x (resolved 3.2.7). `npm audit` identified critical tinypool advisories and mocker advisories. The selection was not accepted merely because tests ran. The package engine and Vite peer requirements were checked with `npm view`, and the [official Vitest guide](https://vitest.dev/guide/) was consulted. The dependency was replaced with Vitest 5.0.5 on Node 22.20 and Vite 6.4.5. Frontend tests and production build passed afterward.

The production dependency audit currently has zero advisories. Four moderate development-only advisories remain in the inherited Tailwind/PostCSS tooling chain; a broad major framework upgrade was outside the chosen change. See `evidence/production-dependency-audit.json` and the committed lockfile. This is not a claim that every possible dependency vulnerability has been eliminated.

## Generated tests were also verified

An exact-text browser locator initially missed the evidence control because its accessible label includes skill-specific screen-reader text. The test was corrected to operate the actual summary element; the behavior assertions were retained. The accessibility scan found a real contrast violation and the color was fixed. Eager-load CI found a real WebSocket constant inflection mismatch and the mapping was fixed while eager loading remained enabled.

## Proof that the suite detects a code regression

On scratch branch `proof/seeded-fitgap-fault`, subtraction in the comparison delta was replaced by addition. The focused suite ran 35 examples and produced 28 failures. The fault was committed at `1ca12dc1551e52ad0c2d99a6e85a1cca8e93c0ec`, then reverted at `1426ef547306b542d7d2a1cad62bc5bf969ba5de`. The branch was pushed so history is reviewable. No assertion was weakened or removed. The final feature branch uses subtraction and the final backend suite passes.
