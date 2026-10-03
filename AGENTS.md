# Subtitula workspace guide

This directory is a workspace containing two sibling Git repositories. It is not itself a Git repository:

- `subtitula-gal`: Next.js frontend. `develop` is hosted development; `master` is production.
- `subtitula-gal-api`: Spring Boot API. `develop` is hosted development; `main` is production.

Run Git, dependency, test, and build commands from the relevant child repository. Check both worktrees before cross-repository work and preserve unrelated or uncommitted user changes. Hosted development was suspended on 21 September 2026 at the user's explicit request for cost control. The API container is confirmed suspended and stopped; processor schedules, all three public/preview routes and GitHub development deployment gates are disabled. DB/R2/secrets and subscriptions are preserved. Resume only on a new user request. Read `subtitula-gal-api/docs/operations/hosted-suspension-2026-09-21.md` for current evidence. The 10 September capability rollout remains historical functional evidence; production stays gated, institutional pilot requirements remain outstanding, and new payments require explicit authorization.

## Local end-to-end development

Start and stop the complete stack from the frontend repository:

- Native Windows PowerShell: `.\start-up.ps1` and `.\start-up.ps1 stop`.
- Linux or WSL 2: `./start-up.sh` and `./start-up.sh stop`.
- Do not use the Bash launcher from native Windows or WSL 1. The Maven wrapper and shell scripts must keep LF line endings; `.gitattributes` enforces this.

Docker Desktop must be running. The launchers start PostgreSQL and Mailpit from the API Compose file, then the API and frontend. Default endpoints are:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8080`; health check: `GET /ping`
- PostgreSQL: `localhost:5432`
- SMTP capture: `localhost:1025`
- Mailpit inbox: `http://localhost:8025`

API routes are rooted directly at paths such as `/ping`, `/register`, and `/projects`; do not invent an `/api` prefix. Local API configuration lives in the ignored `subtitula-gal-api/.env`, copied from `.env.example`. Frontend local configuration lives in the ignored `subtitula-gal/.env.local`. Never put secrets in chat, Git, docs, `NEXT_PUBLIC_*`, or committed workflow files.

The Spring profiles have distinct contracts:

- `local`: Docker PostgreSQL 17, Mailpit, localhost URLs, non-Secure session cookie.
- `dev`: Cloudflare Container on the free `workers.dev` hostname plus an isolated PlanetScale PostgreSQL development branch, `EMAIL_PROVIDER=disabled`, `EMAIL_DELIVERY_REQUIRED=false`, Secure cookie. Email actions fail visibly in logs; use local Mailpit for email E2E.
- `prod`: the same Container image plus an isolated PlanetScale PostgreSQL production branch and Cloudflare Email Service credentials, `EMAIL_DELIVERY_REQUIRED=true`, Secure cookie. Production stays gated until a custom domain is purchased and onboarded.

`dev` and `prod` are Spring profile labels that both inherit `application-hosted.yml`. Never add environment-specific Java code or duplicate hosted configuration between them. Build one immutable API image and promote the same digest; select resources only with runtime environment variables and secrets.

The live PlanetScale resource is database `subtitula`, default branch `development`, PS-5 single-node in `gcp-europe-west1` (Belgium), billed through Cloudflare. PlanetScale technically classifies its default branch as production-capable, but this branch is application development only and must never receive real production data. The branch-scoped role is `subtitula_app_dev`; its current password is installed only as a Cloudflare Worker Secret. The short-lived GitHub bootstrap copies were deleted after the successful deployment. Reset the role again if a human-managed Bitwarden recovery copy is required; never extract the current Worker Secret. Do not create production yet. At launch, provision a separate HA production branch/database and role; do not reuse the development credentials.

On this Windows machine the verified PlanetScale CLI is `%LOCALAPPDATA%\Programs\PlanetScaleCLI\pscale.exe`. OAuth login supports remote device approval with `auth login --format json`. `pscale role get/reset` expects the opaque role ID returned by `role list`, not the display name. Never print `role create/reset` output: it contains the one-time password.

Local Compose names its database volume `postgres17-data` because PostgreSQL data directories are not portable across major versions. Preserve/dump an old PostgreSQL 16 volume instead of mounting it into 17 or deleting it blindly. Both launchers must retain bounded readiness checks that show logs on failure.

Mailpit deliberately never sends real mail. Google OAuth still requires a Web application client, and ElevenLabs transcription requires a real non-production API key even locally; use a restricted/free-tier key.

Google OAuth uses the clients currently named `subtitula-local-current` and `subtitula-development-current`. Other similarly named clients in Google Cloud are historical, unused copies; client names are only labels, while the configured client IDs determine what runs. Do not delete a duplicate until its client ID has been compared with the ignored local env and the installed Cloudflare secret. Hosted dev routes both OAuth initiation and the exact callback `https://subtitula-web-dev.s-counago00.workers.dev/backend/login/oauth2/code/google` through the same-origin gateway. `GOOGLE_REDIRECT_URI` is runtime configuration, not environment-specific code.

## Verification

Frontend, from `subtitula-gal`:

```powershell
npm ci
npm test
npm run build
```

API, from `subtitula-gal-api`:

```powershell
.\mvnw.cmd -B test
```

Use `./mvnw -B test` on Linux/WSL 2. API integration tests use Testcontainers, so Docker is required.

## Infrastructure direction

Keep the hosted platform Cloudflare-first:

- Next.js on Cloudflare Workers using OpenNext.
- The existing Spring container on Cloudflare Containers, with secrets supplied by Workers Secrets or Secret Store.
- PlanetScale PostgreSQL provisioned from Cloudflare, with isolated dev/prod branches and credentials. This preserves the same JPA, JDBC, Flyway, Spring Session, SQL, and tests used locally. PlanetScale operates/supports the database, while its usage appears on the Cloudflare invoice.
- Hyperdrive is not in the Spring database path: its connection string is a Workers-only binding and it does not host PostgreSQL. Reconsider it only if a Worker later queries PostgreSQL directly.
- Cloudflare Email Service is the only future hosted transactional-mail provider. It requires a sender domain, so pre-domain hosted dev deliberately disables delivery; local mail remains Mailpit and there is no AWS/SES or Mailtrap fallback.
- Current public development names use `subtitula-web-dev.<account-subdomain>.workers.dev` and `subtitula-api-dev.<account-subdomain>.workers.dev`. A custom domain is a launch annex, not a deployment prerequisite. When it is bought, change routes and environment URLs, not application code.
- Build the dev frontend with `NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED=false`; this hides verification and recovery affordances while leaving registration/login and all app functions usable. Local and future production use `true`.
- Build the dev frontend with `NEXT_PUBLIC_GOOGLE_AUTH_ENABLED=true`; Google OAuth is routed through the same-origin gateway. Local also uses `true`.
- The hosted `/backend/*` gateway must call `subtitula-api-dev` through the `API_SERVICE` Cloudflare service binding. A public `fetch()` between Workers on the same `workers.dev` zone fails with Cloudflare error 1042. Keep `API_ORIGIN` only to construct the upstream URL and as the `next dev`/unit-test fallback.
- Cloudflare R2 for future durable video/font/artifact storage. Never put durable data on a Container filesystem; its disk is ephemeral.

Cloudflare Containers are managed container compute, not a traditional general-purpose VPS. Requests are routed through a Worker, instances can scale to zero, and all disk is ephemeral. The measured dev scale-from-zero request is roughly 24 seconds; do not mistake a short client timeout for a broken gateway. The Spring Container connects directly to PlanetScale over PostgreSQL/TLS; never run PostgreSQL inside the Container or use R2/FUSE as a database volume.

Frontend tests must explicitly stub public feature flags when they assert enabled or disabled behavior. Do not let `NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED` or `NEXT_PUBLIC_GOOGLE_AUTH_ENABLED` inherit from the CI deployment environment.

For a fast handoff, read `last_session.md` first. Before changing hosting, deployment, or secrets, read the canonical runbooks at `subtitula-gal-api/docs/operations/environment-contract.md`, `subtitula-gal-api/docs/operations/secrets-setup.md`, and `subtitula-gal-api/docs/operations/cloudflare-architecture.md`.

Before changing institutional sessions, durable media, transcript review, agenda
alignment, structured guides, publication, public transparency, or search, read the
complete canonical plan at
`subtitula-gal-api/docs/product/transparency-evidence-search-implementation-plan.md`.
Its minimal-human-review constraint and phase gates supersede older plan fragments.
