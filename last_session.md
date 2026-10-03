# Last session

## Current handoff — 23 September 2026 — institutional fixes implemented

Implemented the user's authorized F0-A/F0-B fixes and part of F1 across two draft
PRs targeting develop:

- Frontend https://github.com/s-counago/subtitula-gal/pull/2, branch
  `fix/institutional-transcript-outputs`, commit `35ace8e`, clean worktree
  `work/institutional-frontend`. GitHub verification is green for that commit.
- API https://github.com/s-counago/subtitula-gal-api/pull/2, branch
  `docs/claims-evidence-integration`, commit `7cc0bd4`, clean worktree
  `work/claims-evidence-design-api`. This PR now includes the backward-compatible
  explicit `clearSpeaker` fix alongside the existing architecture documents.
  Its new GitHub verification was still running at this handoff check.

Read [implementation and remaining scope](work/institutional-frontend/docs/institutional-transcript-outputs.md).
Reviewed transcript is now authoritative for institutional preview, downloads and
public captions. Transcript access survives review completion; unflagged passages
can be corrected; frozen revisions offer SRT/VTT/TXT without publication or optional
analysis. Added recoverable loading errors, true lifecycle labels, document metadata
and permission, versioned/precise public links, search paging and more source context.
Current-version links retain server search; historical versions use local literal
transcript search to avoid mixing versions. API must be deployed before frontend
when the user explicitly resumes hosting.

Validation: 326 frontend tests, Next.js build, OpenNext/Wrangler dry-run, 85 API
Testcontainers tests, and Chromium local UI checks using synthetic API responses
and seekable WAV audio. Native VTT parsed, currentTime reached 1.5 seconds, edit →
freeze → download preserved the correction, mobile 390px had no horizontal overflow,
and there were no JavaScript errors. Evidence is in
`work/institutional-browser-check` and the `work/institutional-*.log` files.
A pre-existing ESLint error and warning are documented. No real-media/hosted E2E or
user-task study was performed; the institutional pilot is not graduated.

### Next development task — complete F1

The user explicitly asked to record the unfinished F1 work after clarifying that
the previous implementation stopped with F1 only partially complete. Deferring it
was the assistant's scope decision, not a user-requested exclusion or a blocker
from Jev. This follow-up records the work; it does not start implementation.

- **F1-A — daily institutional operation:** allow editing metadata of existing
  sessions; complete management of documents already saved, including editing,
  removal and publication permission. Real lifecycle labels and document creation
  with metadata/explicit permission are already implemented.
- **F1-B — public transparency:** support archive filtering without a text query,
  speaker/agenda filters within a session, and full server-side search of historical
  publications. Paging, richer source information and version/instant links are
  already implemented; historical search currently filters transcript text locally.
- **Validation still due:** accessibility and operator/citizen usability with a
  representative long recording, plus regression coverage for the added API/UI
  contracts and separation of publication versions. Synthetic browser checks do
  not complete this validation or graduate the institutional pilot.
- **Related follow-up:** represent concurrent analysis/job states when extending
  the current single-job processing contract.

Complete the frontend and API portions together, preserving minimal human review.
This work does not depend on Jev access or require reactivating hosted development.
Use the two existing PR worktrees above and consult the canonical implementation
plan before changes; preserve the original checkouts' unrelated modifications.

Claims/corpus/Luna API/Jev remain separate design work. Luna in the application must
use the OpenAI API, not the ChatGPT account. Jev means TypeSafe AI.

Original frontend/API checkouts and their pre-existing changes were preserved.
Hosted development remains suspended. GitHub DEPLOY_ENABLED is false in both repos
and API PROCESSING_DEPLOY_ENABLED is false, re-read on 23 September. No hosted
endpoints, inference, purchases, secrets or deployment were triggered. The temporary
Next.js server and headless browser used for verification were stopped.

## Current handoff — 23 September 2026 — Luna evidence experiment

The user explicitly authorized Luna through the ChatGPT subscription **for this
isolated experiment only** while Jev/TypeSafe access is unavailable. Future integrated
assessment remains TypeSafe over API; the application extraction/API design is unchanged.
Completed [28 real evaluations](labs/jev-evidence/reports/resultados-luna-suscripcion.md)
with requested `gpt-5.6-luna` xhigh: 24 frozen fixtures and four additional real-claim
evaluations with automatic retrieval over the seven complete saved source documents.
The [protocol](labs/jev-evidence/docs/luna-suscripcion-experimento.md) records the
subscription-only exception and commands. No Jev inference was made.

Curated passages: 3/3 scored real claims and 20/20 controls match the frozen assistant
reference; R03 remains unscored and Luna abstains. This is label agreement, not complete
response correctness: F10/F11 contain translated/nonliteral AEAT quotes and guards block
both. Ten positive/negative proposals remain. F10 would also fail the single-source
relation gate because its support requires combining tariff and VAT evidence.

Retrieval indexes 244 PDF pages + four HTML snapshots into 853 chunks using BM25,
top six, maximum two per document. Real scored end-to-end agreement is 2/3: R02 becomes
insufficient because retrieval finds the EUR 700,000 allocation but misses the increment
passage. R03 misses the primary budget entry; R04 misses AEAT and remains insufficient.
No reference label/passage influences retrieval ranking or is exposed as an answer key.

Usage: 103,479 input + 14,072 output = 117,551 tokens, including 1,792 cached input and
9,602 reasoning output. Successful invocation times sum to 368.55 s; median 9.63 s for
curated and 16.83 s for retrieved. Subscription limits, no reported API charge or TypeSafe
price extrapolation. All 28 completed with no tool activity or unknown usage. Thirty
local tests pass; frozen inputs, raw/events hashes, usage and offline replay verified.
The first v1 attempt failed at local login checking before model invocation; preserved.
v2 fixes the exec-only flag incorrectly supplied to login status, with no model/prompt change.

Current entry point: from `labs/jev-evidence`, run `python scripts/luna_subscription_v2.py
replay --run-id luna-subscription-v2` to reproduce without inference. Inputs/code frozen
under `alternatives/luna-v2`; responses/receipts under `runs/luna-subscription-v2`.
Recommended next work: cite stored passages by ID rather than generated text; improve
retrieval of increments/phase/conditions and assess new held-out claims; test composed
evidence gates. No application code, PR, hosting, secrets, purchase or publication changed;
both original worktrees' pre-existing changes are preserved and hosted dev stays suspended.

## Historical handoff — 23 September 2026 — frontend readiness

Updated [draft API PR #2](https://github.com/s-counago/subtitula-gal-api/pull/2), now
**docs: integrar afirmaciones y planificar las tres vertientes del frontend**,
with commit `35c3882` on `docs/claims-evidence-integration`. The isolated worktree is
still `work/claims-evidence-design-api`; it is clean after push. Read the
[three-surface frontend audit](work/claims-evidence-design-api/docs/product/frontend-readiness-2026-09-23.md).

The user asked how far the creator, institutional operator and public transparency
frontends lag the existing backend. All eight existing capabilities have frontend
consumers; the main gaps are workflow coherence and presentation. Creator editing
and caption export are largely covered. Modern institutional exception review lacks
download and persistent transcript access after completion. The preview uses a
separate state: a local execution of the real `transcriptWords` function projected
original `San Pedro` even when the reviewed segment said `San Paulo`. Public video
has no captions track. Dashboard states, metadata editing, document fields/permissions,
filters, pagination and historical-version links also need work. Several require
API additions; claims/corpus/Jev remain new backend and frontend work, not mounted
features awaiting a screen.

Recommended frontend sequence: F0-A reviewed transcript/preview coherence and errors;
F0-B institutional download and public captions; F1 daily operation and citizen
navigation. Then integrate the RFC's private replay and later inference. The RFC,
decision log and canonical plan now link this assessment. No implementation or
phase graduation in this task. Luna remains OpenAI API only; Jev is TypeSafe AI.

Verified 23 September: frontend 309 tests/50 files passed (non-failing jsdom
navigation warning), frontend production build passed, API 85 tests passed with
local PostgreSQL/pgvector Testcontainers. Validated 27 relative links and 20 frontend
references pinned to commit `8bee2b3`. API base is `a0b8cde`; both match origin/develop.
No browser E2E or user-task study was performed. Prior PR commit's CI is green;
verification for `35c3882` was in progress when checked after push.

Original frontend/API checkouts and all their prior changes remain untouched.
Hosted development stays suspended; no new provider calls, secrets, purchases or
runtime/deployment changes. Audit scope is uploaded recordings and later
transcription. Optional clarification of whether "transmission" meant live remains
pending; streaming/live captions would be a separate product scope.

## Historical handoff — 22 September 2026 — claims integration design

Opened [draft API PR #2](https://github.com/s-counago/subtitula-gal-api/pull/2)
against `develop`: **docs: plan de integración de afirmaciones con Luna API y Jev**.
Branch `docs/claims-evidence-integration`, commit `e78021a`, isolated worktree
`work/claims-evidence-design-api`. The PR contains five documentation files only.
Read the [architecture proposal](work/claims-evidence-design-api/docs/product/claims-evidence-integration-plan.md)
and [portable lab baseline](work/claims-evidence-design-api/docs/product/claims-evidence-lab-baseline-2026-09-22.md).

The user explicitly confirmed **Luna through the OpenAI API, with application API
credentials and no ChatGPT account/subscription authentication**. Preserve the Luna
xhigh choice. Jev means **TypeSafe AI's evaluator**; access is still unavailable.
The existing lab's Codex transport is historical evidence, not the production adapter.

Recommended design: optional extraction/corpus/assessment jobs in existing Spring
and processor, PostgreSQL domain state, R2 artifacts, immutable source versions,
closed evidence bundles, provider-attempt accounting and private editor integration.
Do not let auxiliary failures fail the project or block transcript publication.
The first proposed implementation is private replay tied to a frozen revision with
owner checks and an exact minute link; no Jev key needed. The current task is planning,
not implementation. Public assessments, shared corpus, global matter identities and
chat remain gated/deferred as documented; the canonical pilot phase is unchanged.

Validation: 85 API tests passed with local Testcontainers; all 16 offline Jev lab
tests passed; 13 relative links, eight source hashes and diff whitespace checked.
The PR's GitHub verification was in progress when created. No model inference,
secret installation, purchase or hosted endpoint call. Development/processing gates
were read and remain false. Hosted development remains suspended. Original API and
frontend worktrees and all their pre-existing changes were preserved.

## Earlier handoff — 22 September 2026 — Jev fixtures

**Latest follow-up — offline fixtures and failure mitigation:** the user asked to
prepare multiple fixtures while awaiting the Jev key. The lab now has
[24 semantic fixtures and 10 technical scenarios](labs/jev-evidence/fixtures/v2/README.md),
with four original extractions, twenty controlled variants and a separately frozen
assistant reference. R03 is exploratory and excluded from scoring because program
identity remains uncertain. The [failure mitigation plan](labs/jev-evidence/docs/mitigacion-fallos-jev.md)
distinguishes implemented controls from future work and sets evaluation gates.
The [preparation report](labs/jev-evidence/reports/fixtures-v2-preparacion.md) separates
illustrative token/cost scenarios from unmeasured accuracy/latency. Local preflight
can skip 3/24 calls; confidence 0.85 is provisional, not calibrated. Sixteen offline
tests pass, including ten simulated transport failures. No Jev inference was made
and no new key is needed to inspect or test the fixtures.

When the key is saved locally, prefer `python scripts/benchmark.py run --selection
smoke --run-id fixtures-v2-smoke` from the lab, then the documented full run. The new
runner uses the direct TypeSafe API only, separates real/control metrics, preserves
errors and unknown consumption, and supports offline replay. Smoke plus full uses
up to 30 calls because caches are per run. Original v1 inputs and runner are preserved;
the earlier 11-case next step below is superseded by the new smoke/full protocol.

**Earlier work — initial Jev experiment:**

The user requested a separate Jev/TypeSafe AI experiment to compare existing extracted
claims with public sources. [The isolated lab](labs/jev-evidence/README.md) is prepared
under `labs/jev-evidence`: four unchanged Luna xhigh claims from the Vigo 23 December
2025 transcript, seven public sources with snapshots and hashes, seven synthetic/ablation
controls, frozen assistant-authored reference, 11 prepared requests, direct TypeSafe and
Cloudflare adapters, receipts, token/cost reporting and offline replay. Read the
[report](labs/jev-evidence/reports/viabilidad-y-preparacion.md) and
[integration proposal](labs/jev-evidence/docs/integracion.md).

**Real Jev inference has NOT run.** Eight local tests passed using temporary mocked
responses; these are not model results. The direct runner stops before network access
because `TYPESAFE_API_KEY` is unavailable. The TypeSafe console requires login. Cloudflare
AI Gateway credit/gateway reads returned 403, so credit balance is unknown. The user was
asked asynchronously for a key saved privately in `labs/jev-evidence/.env` or confirmation
of existing AI Gateway credits. No response has arrived yet. Do not purchase credits or
raise quotas without explicit authorization. Once access is available, run the prepared
11-case protocol and report measured results, preserving failures and the frozen reference.

The corpus demonstrates an important comparison pitfall: Sogama's reduced 2025 tariff
of EUR 95 plus 10% VAT equals EUR 104.50. That alone does not establish the prior EUR 86
or the tariff actually applied to Vigo. The runner computes arithmetic conditionally in
Python and leaves substantive assessment to Jev. Preliminary documentary labels are
assistant assessments, not independently human-reviewed ground truth.

No new transcription, app-code change, deployment, purchase or commit. Both application
worktrees' pre-existing changes are preserved. Hosted development remains suspended as
recorded below. Product phase gates are unchanged.

## Current handoff — 21 September 2026

Hosted development is suspended again at the user's explicit request for cost
control. Container suspension and actual stopped state were verified; both
processor schedules and all three public/preview routes are disabled. GitHub
deployment gates are false in both repositories and development environments,
including processing. DB/R2/secrets and subscriptions are preserved. Resume only
on a new user request. Read
[the shutdown record](subtitula-gal-api/docs/operations/hosted-suspension-2026-09-21.md).
Manifest changes are local/uncommitted. Billing review awaits Cloudflare browser
sign-in; the infrastructure OAuth token cannot read billing history (HTTP 403).

## Current handoff — 12 September 2026

**Latest discussion — Luna xhigh selected; citizen search explored:** the user chose
Luna xhigh for cost/quality and asked how claims should support the transparency portal.
Read [the exploration](labs/claims-pipeline/ideas/de-afirmaciones-a-respuestas-2026-09-12.md).
It proposes source passages plus derived claims/matters and rebuildable search projections;
retrieve from both paths and present intent-specific, attributed results with evidence.
Partial claims are retrieval clues, not assumed reliable structured facts. A conversational
mockup uses three prepared examples from the Vigo transcript; it is not live search or
new model inference. Proposed next test: passages only versus claims only versus both,
on citizen questions. No application code, infrastructure, frozen experiment, deployment,
or canonical phase gate was changed.

**Latest work — Sol medium comparison completed without the proposed improvements:**
the user explicitly requested the same process. The isolated lab reused v1 inputs,
prompts, schemas, validation and the frozen reference through `gpt-5.6-sol` medium.
Read [the report](labs/claims-pipeline/reports/resultados-sol.md) and
[protocol](labs/claims-pipeline/docs/comparacion-sol.md). Result: 16/25 faithful,
6 partial, 0 incorrect directed matches and 3 missed, compared with 9 faithful for
Luna low and 12 for xhigh. This is reference recovery, not global output precision.
Seven operations, including one allowed context round, saved 69 final candidates
without technical rejections or exact duplicates; 32 matters, 35 mentions, 73 citations.
The ambiguous `desa gama` amount remained omitted after context retrieval.
Runtime: 649.365 seconds. Usage: 62,547 input (2,432 cached) + 30,989 output = 93,536
tokens, including 11,270 reasoning tokens within output. API-price equivalent:
USD 0.8612128; actual runs used subscription limits. No retry or separate Sol probe.
Initial inputs matched GLM and both Luna runs; all hashes, saved-response replay,
usage receipts and double-import checks passed without new inference. No extraction
improvements, transcription, app integration, deployment or commit were performed.
[Explorer](labs/claims-pipeline/reports/explorador-sol.html).

**Previous work — Luna low/xhigh comparison completed:** the user asked for an extra-high
pass, token comparison and pricing. Read [the report](labs/claims-pipeline/reports/resultados-luna-xhigh.md)
and [protocol](labs/claims-pipeline/docs/comparacion-luna-xhigh.md). The completed xhigh
pass preserves all initial inputs and the 25-case reference: 12 faithful, 7 partial,
0 incorrect directed matches and 6 missed, versus low's 9/5/0/11. It saved 89 of 100
candidates, rejected 11 and produced no exact duplicate records; 25 matters and 41 mentions.
Six operations consumed 43,285 input + 94,428 output = 137,713 tokens, including
73,766 reasoning tokens within output. Low used 40,952 total, including 550 reasoning.
Runtime: 1,725.615 versus 152.631 seconds. API-price equivalents: USD 0.1219706 versus
0.0154614; actual runs used subscription limits. A first xhigh attempt hit the local
360-second limit without usage or a final response, and is preserved as interrupted;
its unknown consumption is excluded. After inspection, the completed attempt used
a 900-second limit. Both small transport probes are also counted separately.
Offline replay and double-import checks passed without new inference. No transcription,
app/infrastructure change, deployment or commit. [Explorer](labs/claims-pipeline/reports/explorador-luna-xhigh.html).

**Previous work — Luna comparison completed using the existing ChatGPT subscription:**
the user asked to repeat the GLM pass with Luna. The isolated lab now runs the same
v1 workflow through official Codex CLI 0.153.4 with `gpt-5.6-luna`, low reasoning.
Read [the comparison report](labs/claims-pipeline/reports/resultados-luna.md) and
[the protocol](labs/claims-pipeline/docs/comparacion-luna.md). The unchanged 25-case
reference gives nine faithful, five partial, zero incorrect directed matches and
11 missed cases. An additional semantic error appears outside those positives.
Six model operations saved 28 candidates, rejected two literal-quote failures and
produced zero exact duplicates; runtime was 152.6 seconds. There was one separate
empty-input transport check. No second transcription, API-key billing, app change,
deployment or commit. The original GLM run and frozen reference remain intact;
identical initial extraction payloads and offline/idempotent replay were checked.
The local explorer is [Luna](labs/claims-pipeline/reports/explorador-luna.html).

**Latest work — isolated real claims experiment completed:** the user authorized a
standalone lab, ElevenLabs transcription, a Sol/Astra reference review before GLM,
and a first actual extraction comparison using GLM only. Everything lives in
[labs/claims-pipeline](labs/claims-pipeline/README.md), outside both application repos.
Read [the result report](labs/claims-pipeline/reports/resultados.md) and
[the diagram/pseudocode](labs/claims-pipeline/docs/pipeline.md).
The complete Vigo 23 December 2025 recording (26:55) yielded 4,356 words and 67 segments;
the existing ElevenLabs key worked within its configured cap (1,795 credits reported).
Sol and the root assistant reviewed 25 positive cases and six controls, frozen before
any GLM call. The seven-call GLM v1 run stored 56 candidate records, including 33 exact
duplicates, and rejected eight candidates. Against the reference: zero fully faithful,
five partial, two incorrect and 18 missed. This version is not ready for integration.
Generation at catalog rates is estimated at USD 0.00890466; not an invoice. Cached
responses replay offline and double import does not duplicate operations. No new
provider, subscription, quota increase, app-code change, deployment or commit occurred.
Next: review the documented failures and design a smaller, simpler extractor; preserve
the frozen reference and v1. Source diarization S0026–S0028 is also known to be flawed.

**Previous discussion — claim identity, context and repeatable experiments:** the user
prefers approach 2 (bounded low-cost LLM plus validation), starting with existing GLM,
and prioritizes avoiding incorrect data. Read the [clarifications and experiment ideas](subtitula-gal-api/docs/product/afirmaciones-aclaraciones-y-ensayos-2026-09-11.md).
Claims and occurrences have separate identities; evidence remains mandatory; further
authorized transcript context can be retrieved; structured proposals pass application
validation before persistence/public acceptance. DeepSeek-V4.1-Flash direct-API prices
and cache semantics were checked; no inference calls or new provider purchases occurred.
Document/news verification is explicitly deferred in [the future scope](subtitula-gal-api/docs/product/afirmaciones-cotejo-documental-futuro.md)
and backlog CLAIM-DOC-01. The 45k-token session remains an illustrative assumption,
not a measurement. Next: discuss the proposed corpus and repeatable small experiments;
no automatic continuous processing or implementation is started. Earlier work is preserved.

**Latest follow-up — exploratory report, before implementation planning:** the user
requested an explanatory document about persistent speaker profiles, explicit claims,
a shared catalogue of matters, repeated statements and evidenced contradictions.
Read [the exploration report](subtitula-gal-api/docs/product/afirmaciones-asuntos-informe-exploratorio-2026-09-11.md).
It walks through fictional transcript examples, semantic candidate retrieval versus
matter identity, uncertainty and deduplication, low-cost model options, hypothetical
token costs and proposed experiments. Sources/prices checked on 11 September; no
inference experiment, feature implementation, deployment or new provider purchase.
Next: let the user review and discuss the ideas before turning them into a delivery
plan. The natural-language search work below is still pending. Documentation remains
local and uncommitted; earlier diagram/search documentation changes are preserved.

**Previous follow-up — natural-language search remains incomplete:** the user's exact
question `quién habló de las pérdidas de las tuberías del agua?` returned HTTP 200 /
HYBRID / zero results despite relevant evidence. Short Spanish topic queries returned
seven search documents. There is no dedicated “who” grouping, and the synthetic
speaker remains unidentified. See the [diagnostic and next development slice](subtitula-gal-api/docs/product/natural-language-speaker-search-2026-09-10.md).
NLS-01–NLS-06 are proposed acceptance criteria, not implemented or passing tests.
Next: question-intent/topic handling, evidence retrieval and speaker grouping; evaluate
both languages, multiple speakers and absent topics. The 16/16 score below covers only
the previous synthetic set. Documentation updated; no search implementation, deployment,
credential or capability change. Diagram/documentation edits remain local and uncommitted.

**Development resumed and all eight capabilities are enabled by the user's explicit request.**
Read [the complete rollout evidence](subtitula-gal-api/docs/operations/capability-rollout-2026-09-10.md). The 8 September suspension below
is historical. Public development routes and processor Cron are active; previews
remain off. Production stays gated and no new payments or production resources
were created. Galician is the default and Spanish the only alternative.

Both integration PRs were merged into develop after passing GitHub verification.
Development deployment gates are re-enabled at repository/environment scope,
including asynchronous processing. The API deployment applies each image through
the authenticated development restart/readiness control. Final credential rotations
are reserved for the user; the existing operations credential is also installed in
the GitHub development environment. Never print ignored recovery material.

Verified: actual R2 upload, ElevenLabs/webhook transcription, duplicate/retry/abort
boundaries, Range playback, exception review, automatic agenda and cited guides,
anonymous publication, immutable correction, withdrawal and both search modes.
Galician public version 2 and Spanish public version 1 remain available.
Hybrid threshold 0.48 improves principal task success from 13/16 to 16/16; the
additional set improves 6/10 to 9/10. All ten no-answer cases are correct, no request
failed, and hybrid warm p95 is below 2.4 seconds. One specific reply remains outside
the top 20 on the additional set. These synthetic results do not graduate the real
institutional human-time, accessibility, load, restore or governance pilot.

Validation: 85 API, 45 processor and 309 frontend tests; Worker typechecks; builds;
4 search evaluator and 2 offline production configuration tests. Windows Docker
startup recovery preserves data volumes. Future production configuration is generated
offline with isolated resources and a pinned approved image; see the domain launch
annex. No domain, HA production database, sender or production credentials exist yet.
Keep Omarchy work separate. Review the remaining field-pilot gates before launch.

### Final deployment confirmation — 20:18 UTC

Both development deployments and the latest API verification finished successfully:
[API deploy](https://github.com/s-counago/subtitula-gal-api/actions/runs/34524791360),
[API verification](https://github.com/s-counago/subtitula-gal-api/actions/runs/34524791488),
[frontend deploy](https://github.com/s-counago/subtitula-gal/actions/runs/34524556315).
API revision `a0b8cde` deployed Worker `c8de0358-e486-4de9-aa0c-cd04c97b068f`
and image `sha256:5dad5830e1f79a4f4375b9d98a802e681bbca94f1121b6e4c33cf004729a23f0`;
processor `61633283-1b43-49be-8d21-22113c83aa5a`; frontend revision `8bee2b3`
deployed `b996a0b4-ac51-484f-a2fd-2e17e495f3a7`. The CI container restart
confirmed stopped state, then actual readiness in 28.447 seconds.

After deployment, all four web/gateway/API/processor health requests returned 200;
the runtime capability endpoint returned all eight true. Both primary anonymous
publications returned 200 with no checked private fields, each recording returned
206 for 1,024 bytes, Galician version 1 remained exactly equal to its saved snapshot,
and the withdrawn publication returned 404. All three public routes are enabled,
all previews disabled, and the processor retains its five-minute/daily schedules.
Repository and development-environment deployment gates are true in both repos,
including processing. Both integration PRs are merged; source worktrees are clean.
Docker engine 28.5.1 is healthy. The activation goal is complete; future production
launch and the user's deferred credential rotations remain as documented above.

### Functionality diagrams updated — 10 September 2026

The [interactive control room](subtitula-gal-api/docs/product/subtitula-sala-de-control.html#caps)
and [Mermaid architecture/feature diagrams](subtitula-gal-api/docs/product/architecture-flows.md)
now show all eight active development capabilities, Galician/Spanish scope, current
resources and search/publication behavior, with synthetic evidence and production
gates clearly separated. Both repositories link to the shared diagrams; the canonical
phase table is current. Documentation changes only; no deployment or credential change.
All 9 channels / 66 steps and controls passed local DOM checks. Browser policy blocked
the local file preview, so visual layout inspection remains unverified.

## Historical checkpoints — 8 September 2026

**Latest handoff: hosted development remains suspended by user request.**
Local stack/Docker are stopped. Cloudflare processor schedules (every five
minutes and daily) were removed through its API and a live read confirmed an
empty list. Development `triggers.crons: []` is committed and pushed: deploying
the current configuration keeps them off, but an older configuration containing
schedules can restore them. All three development public/preview URLs are off;
GitHub deployment gates are false at repository and development-environment scope.
**The latest container check still showed running: shutdown is not confirmed.**
Its ten-minute idle timeout and up-to-fifteen-minute Cron propagation are not a
guaranteed shutdown deadline. Preserved DB/R2/secrets; subscriptions not cancelled;
the $5 Workers plan is not a spending cap. Do not resume automatically.
See the detailed suspension checklist in
[the versioned handoff](subtitula-gal-api/last_session.md).

**Omarchy compatibility review, later on 8 September:** the user uploaded
`develop-atender`, `feature/navigation-shell-atender`, and
`worktree-posthog-redesign-atender` to the frontend remote. See
[the compatibility report](work/omarchy-compatibility-20260908.md).
Only `develop-atender` is recommended for integration; an isolated rehearsal
passes 361 tests, build and Cloudflare dry-run after three conflict resolutions.
Original branches remain untouched; capture fixtures and mobile styling need
the adjustments documented in the report. Omarchy is no longer missing remotely.

**Updated:** 8 September 2026 (Europe/Madrid)

**Local activation after recovery:** at the user's request,
`CAPABILITY_DURABLE_INSTITUTIONAL_UPLOAD=true` is now set in this workspace's
ignored `subtitula-gal-api/.env`. Restart/start the local stack to load it.
No hosted flag was changed. The recovery report's earlier local-flag comparison
describes the state before this activation; end-to-end checks remain pending.

Read [the versioned API handoff](subtitula-gal-api/last_session.md) and
[the consolidated Claude recovery](subtitula-gal-api/docs/operations/continuity-2026-09-08.md).

The September commits from `C:/Users/Sejio/subtitula` have been recovered into this
workspace's `feature/transparency-evidence-search-integrated` branches. The branches
are the backup target; develop and production have not been pushed or deployed.
Local env files, keys and data differ between the two Windows clones.

Next: finish the local durable-upload checks, then prepare hosted resources/secrets
and activate one capability at a time. See the report for the exact eight-capability
and credential tables. Omarchy's separate navigation/coherence work is now available
on remote branches and reviewed, but not integrated into the primary worktree.

The diagrams previously outside Git are now versioned under
`subtitula-gal-api/docs/product/architecture-flows.md` and
`subtitula-gal-api/docs/product/subtitula-sala-de-control.html`.

## Capability rollout live progress — 8 September 2026

User requested activation of all remaining capabilities in development. Goal remains active; no new hosted capability flag has been enabled yet.

- Cloudflare Wrangler OAuth is valid for the configured account.
- Created private R2 bucket `subtitula-media-dev` (weur hint), applied repository CORS, verified public r2.dev access disabled.
- PlanetScale login renewed. Backup `capabilities-rollout-20260908`, ID `10yur4e45rnd`, completed successfully (8,970,501 bytes; expires 8 October).
- Bitwarden unlocked by user. ElevenLabs development key is enabled, STT-only, 5,000 credits per refresh. `/v1/user` returns `missing_permissions` (user_read), NOT proof of an expired key. Real STT remains to test.
- Created ElevenLabs transcription-completed webhook `408c5225da5340f69e3ed7ae7ff1405b`, targeting processing dev `/webhooks/elevenlabs/speech-to-text`; set its nonsecret ID in processor development manifest.
- Rollout secrets staged only in ignored `subtitula-gal-api/processing-worker/.wrangler/rollout/processor-secrets.json`: development ElevenLabs key, new internal HMAC, webhook signing secret. R2 S3 credentials still missing. This file is NOT yet installed as Worker Secrets. Preserve it until installed/backed up securely; never print it.
- Docker failed on stale `Docker/run/dockerInference`. Per user request disabled EnableInference/EnableInferenceTCP/EnableInferenceGPUVariant in settings-store (backup beside original), preserved runtime directory as `run-before-subtitula-20260908`, restarted Docker successfully: engine28.5.1. Volumes unchanged.
- API suite passed81 tests; processor28 and search-evaluator3 passed. Typegen/typechecks started next.
- Browser handles in current CUA session: vaultTab1262987472, elevenTab1262987482, webhookTab1262987485, cfTab1262987491. Cloudflare tab opened R2 overview to create bucket-scoped S3 credential next.
- Omarchy remains separate, not merged. Main integration branches remain active. Do not publish production.

Rollout continuation checkpoint: processor deployed version5c8b1eed-8a9f-48ca-921f-f48e939d1b1d, all5 secrets installed; API internal HMAC and ElevenLabs development installed. R2 scoped token created and PUT/signed206 Range verified. PlanetScale extensions verified live and V10 confirmed. API commit304b9a2 pushed integration branch; see versioned docs/operations/capability-rollout-2026-09-08.md. API Docker dry-run still running in exec session22821 (downloading Maven dependencies); frontend301 tests passed and OpenNext dry-run running session64760. Do not restart these without checking handles. Synthetic44sec speech fixture saved in ignored processor/.wrangler/rollout/session-demo.wav. No new capability flags yet. Current CUA cfControlled is browser tab1262987491 at newly created S3 token result; secret values hidden by sanitized DOM snapshots, copy buttons nth1 access ID/nth2secret copied into ignored rollout payload. Never print payload. Chrome/Vault already unlocked. Docker now working.

Latest: API dark deployment completed version6b18375f-1831-4082-a411-49925b84a2a9, image digestsha256:f5ddf1bf6887fcf36efcfab4d7c5c618a0276a11f880191868d77edfcb59f2eb. Live PlanetScale now V18 allsuccess; /capabilities returns full contract with only normalizedTranscript=true. First cold/migration request500 was transient; subsequent request200 and DB prove completion. Frontend build/dryrun passed. Actual frontend deployment launched next (see active exec session tool result). Tail API session59265 stilllive writing ignored api-tail.jsonl; avoid logging raw events since they include request metadata. Pilot helper/upload scripts prepared in ignored .wrangler/rollout (not run yet); need enabledurable first then bootstrap/run upload. Remaining 6 downstream flags stillfalse. All new secrets installed; rootnote initial provision entries now superseded.

## STOPPED FOR THE NIGHT — explicit user request
User asked to stop everything and go to sleep. Do not resume capability activation automatically. Local stack stopped with frontend start-up.ps1 stop; Docker Desktop shutdown requested. See versioned docs/operations/capability-rollout-2026-09-08.md for precise saved state. Frontend deployed80dd5d8c; API V18 migrated. Durable flag true in Worker14900a14 and manifest but stillFALSE in running Spring: container must be restarted to apply runtime env. Other new flagsfalse. Synthetic usercreated, NO project/upload/transcription. Secrets remain in ignored processor/.wrangler/rollout; never print. No production changes. Omarchy remains separate.

## HOSTED SUSPENDED — explicit user request
The user then requested remote suspension for cost control. Cron triggers removed, all3 development public/previewURLsdisabled, GitHubDEPLOY_ENABLEDfalse both repos/scopes and processingfalse. No workflowinstances or activeActions. DB/R2/secretsretained, fixedplansNOTcancelled. Do not resume activation without fresh userrequest. See subtitula-gal-api/docs/operations/hosted-suspension-2026-09-08.md for verifiedstate and remaining billing limits.
