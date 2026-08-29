# FranchiseGuard AI

**AI Compliance Intelligence for Franchise Operations** — a mobile-first
RocketRide app for the people who keep a franchise network on-standard.

## What it does

Gives an Area Manager a field companion for franchise standards auditing
(PS-18): capture an inspection from the store floor, let the vision model flag
violations against the Brand Standards Manual, and turn the findings into a
shareable compliance report with a remediation timeline — then track every
location's risk over time and act on the alerts that matter.

## The flow (8 screens)

| # | Screen | What it does |
|---|--------|--------------|
| 1 | **Splash** | Branded load-in with the product line. |
| 2 | **Login** | Area Manager sign-in — email / password, Continue with RocketRide, biometric. |
| 3 | **Home Dashboard** | Network KPIs (compliance score, high-risk stores, pending inspections, stores monitored), today's inspections, compliance trend, risk mix, recent AI alerts. |
| 4 | **Upload Inspection** | Store selector, camera / gallery / video capture, complaint note, a five-point standards checklist, and *Analyze with AI*. |
| 5 | **AI Analysis** | Frame preview with detection bounding boxes, per-violation confidence, severity chips and a risk meter. |
| 6 | **Compliance Report** | Overall risk score, critical / major / minor breakdown, evidence gallery, remediation timeline, recommendation cards, download / share. |
| 7 | **Location Memory** | Per-store history — 90-day risk line, complaint trend, resolved vs. unresolved findings, inspection timeline. |
| 8 | **Manager Alerts** | Priority queue with *Schedule re-inspection*, *Issue cure notice*, *Escalate to legal*. |

Plus **Inspections**, **Reports** and **Profile** tabs on the bottom nav.

## Architecture

- **`src/screens/*`** — one folder per screen, each with its own CSS Module.
  `src/screens/registry.ts` maps a screen name to its component; the app shell
  (`src/app/`) owns navigation, the phone frame, page transitions, the header
  and the bottom nav.
- **`src/components/*`** — a reusable library: primitives (Button, Card, Chip,
  Field, ProgressRing, RiskMeter, SegmentedControl, Sheet, Skeleton), charts
  (hand-built SVG LineChart / DonutChart / BarChart / Sparkline — no chart
  dependency), vision (VisionScene, DetectionOverlay) and domain cards
  (ViolationCard, RecommendationCard, EvidenceGallery, TimelineList, …).
- **`src/lib/ai.ts`** — the simulated intelligence layer: templated findings
  over a violation catalogue, randomised confidence, lifelike async delays.
  Swap these functions for a real RocketRide vision pipeline without touching
  a screen.
- **`src/data/*`** — production-quality mock data: 15 stores, a violation
  catalogue, inspection history, alerts and reports.

## Styling

Plain CSS Modules, one `*.module.css` per component. Design tokens live in
`src/styles/tokens.css` as CSS custom properties scoped to `[data-fg-root]`
(nothing leaks into the shell), with light + dark palettes and a
`prefers-reduced-motion` guard. Brand webfonts (Sora, IBM Plex) attach lazily
via `src/styles/fonts.ts` and degrade to a system stack.

## Development

Open the `.rrapp` file to launch the App Builder: live preview on the Design
tab, identity and packaging on the Package tab, publishing on the Deploy tab.

Platform guide for building apps: `.rocketride/docs/ROCKETRIDE_APPS.md`.
