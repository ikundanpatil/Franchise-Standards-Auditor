# Franchise Standards Auditor (PS-18) — FranchiseGuard AI

**AI Compliance Intelligence for Franchise Operations.**

A mobile-first [RocketRide](https://rocketride.ai) app that gives a franchise
Area Manager a field companion for standards auditing: capture an inspection on
the store floor, let a vision model flag violations against the Brand Standards
Manual, turn the findings into a shareable compliance report with a remediation
timeline, and track every location's risk over time.

Built for the RocketRide Buildathon.

## The flow (8 screens)

| # | Screen | What it does |
|---|--------|--------------|
| 1 | **Splash** | Branded load-in. |
| 2 | **Login** | Area Manager sign-in — email / password, Continue with RocketRide, biometric. |
| 3 | **Home Dashboard** | Network KPIs, today's inspections, compliance trend, risk mix, recent AI alerts. |
| 4 | **Upload Inspection** | Store selector, camera / gallery / video capture, complaint note, five-point checklist, *Analyze with AI*. |
| 5 | **AI Analysis** | Frame preview with detection bounding boxes, per-violation confidence, severity chips, risk meter. |
| 6 | **Compliance Report** | Overall risk score, critical / major / minor breakdown, evidence gallery, remediation timeline, recommendation cards, download / share. |
| 7 | **Location Memory** | Per-store history — 90-day risk line, complaint trend, resolved vs. unresolved findings. |
| 8 | **Manager Alerts** | Priority queue with *Schedule re-inspection*, *Issue cure notice*, *Escalate to legal*. |

Plus **Inspections**, **Reports** and **Profile** tabs on the bottom nav.

## Repo layout

```
apps/franchiseguard-ai-ui/     the app (React 18 + TS, rsbuild Module Federation remote)
  src/screens/                 one folder per screen + registry.ts
  src/components/              reusable library — primitives, SVG charts, vision overlay, domain cards
  src/lib/ai.ts                simulated vision/report engine (swap for a real RocketRide pipeline)
  src/data/                    mock data — 15 stores, inspections, alerts, reports
  src/styles/tokens.css        design tokens scoped to [data-fg-root]
.rocketride/                   platform-vendored docs, catalog, shell/client tarballs (gitignored)
```

## Develop

Requires Node 20+ and pnpm. Connection settings come from `.env`
(see [`.env.example`](.env.example)); the platform populates it on
`rocketride login` or when you connect from the VS Code extension.

```bash
pnpm install
pnpm --filter local-franchiseguard-ai dev      # live App Builder preview
pnpm --filter local-franchiseguard-ai build    # tsc --noEmit && rsbuild build
```

Or open `apps/franchiseguard-ai-ui/franchiseguard-ai.rrapp` to launch the
App Builder (Design / Package / Deploy tabs).

## Deploy

App id `team_franchiseguard.franchiseguard-ai`. Deploy + publish through the
RocketRide SDK (`client.deploy.verifyApp` → `client.deploy.addApp` →
`client.publishApp`) or the Deploy tab. Deploying creates an immutable
registry version; publishing repoints an audience (`@me`, `@team/<name>`,
`@public`) at it.
