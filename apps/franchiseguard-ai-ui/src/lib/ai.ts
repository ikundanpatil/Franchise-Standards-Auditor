// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * The "AI" layer — entirely simulated. It stitches templated language over the
 * violation catalogue, rolls randomised confidence scores, and returns after a
 * lifelike delay so the UI can show progress. Swap these functions for real
 * model calls (e.g. a RocketRide vision pipeline) without touching the screens.
 */

import type {
	AnalysisResult,
	ComplianceReport,
	Detection,
	EvidenceShot,
	Recommendation,
	Severity,
	Store,
	TimelineEvent,
	ViolationType,
} from '../types';
import { VIOLATION_TYPES } from '../data/violations';
import { riskFromScore, scoreGrade, SEVERITY_WEIGHT } from '../utils/risk';
import { makeRef } from './format';
import { chance, clamp, confidence, delay, jitter, pick, randInt, round, sample } from './random';

const MODEL_VERSION = 'fg-vision-2.4';

export const ANALYZE_STEPS = [
	'Uploading evidence to secure store',
	'Normalising frames · white-balance · de-noise',
	'Running FranchiseGuard vision model',
	'Cross-referencing Brand Standards Manual',
	'Scoring severity & rolling up risk',
	'Composing findings',
] as const;

export const REPORT_STEPS = [
	'Collating detections & evidence',
	'Grading against brand thresholds',
	'Drafting recommendations',
	'Building remediation timeline',
	'Finalising compliance report',
] as const;

/** Pick a believable set of violations, biased by the store's current risk. */
function chooseViolations(store: Store): ViolationType[] {
	const pool = VIOLATION_TYPES;
	let count: number;
	switch (store.risk) {
		case 'low':
			count = randInt(0, 2);
			break;
		case 'medium':
			count = randInt(2, 3);
			break;
		case 'high':
			count = randInt(3, 5);
			break;
		default:
			count = randInt(4, 6);
	}
	if (count === 0) return [];
	// Weight critical/major slightly higher for riskier stores.
	const weighted = pool.flatMap((v) => {
		const w = v.severity === 'critical' ? 3 : v.severity === 'major' ? 2 : 1;
		const boost = store.risk === 'low' ? 1 : store.risk === 'critical' ? w : Math.ceil(w / 1.5);
		return Array.from({ length: boost }, () => v);
	});
	const seen = new Set<string>();
	const out: ViolationType[] = [];
	for (const v of sample(weighted, weighted.length)) {
		if (seen.has(v.id)) continue;
		seen.add(v.id);
		out.push(v);
		if (out.length === count) break;
	}
	return out;
}

function explain(v: ViolationType, conf: number): string {
	const lead = pick([
		'Detected with high spatial confidence',
		'Flagged by the vision model',
		'Identified in the uploaded frame',
		'Model attention concentrated here',
	]);
	const tail = pick([
		'Matches known non-conformance patterns from comparable sites.',
		'Consistent with prior findings at similar locations.',
		'No mitigating context detected in surrounding pixels.',
		'Bounding region isolated from active-service cues.',
	]);
	return `${lead} (${Math.round(conf * 100)}%). ${capitalise(v.rationale)}. ${tail}`;
}

function capitalise(s: string): string {
	return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Roll detections + a risk score for a store. Deterministic within a run. */
export function composeAnalysis(store: Store, imageLabel = 'Kitchen line · station 2'): AnalysisResult {
	const chosen = chooseViolations(store);
	const detections: Detection[] = chosen.map((v, i) => {
		const conf = confidence(v.severity === 'minor' ? 0.7 : 0.8, 0.98);
		const [x, y, w, h] = v.box;
		return {
			id: `det-${Date.now().toString(36)}-${i}`,
			typeId: v.id,
			label: v.label,
			category: v.category,
			icon: v.icon,
			severity: v.severity,
			confidence: conf,
			box: [
				clamp(jitter(x, 0.03, 0, 0.9), 0, 0.9),
				clamp(jitter(y, 0.03, 0, 0.9), 0, 0.9),
				clamp(w * (0.92 + Math.random() * 0.12), 0.08, 0.5),
				clamp(h * (0.92 + Math.random() * 0.12), 0.08, 0.5),
			],
			explanation: explain(v, conf),
			standardRef: v.standardRef,
			remediation: v.remediation,
		};
	});

	const rawRisk = detections.reduce((sum, d) => sum + SEVERITY_WEIGHT[d.severity], 0);
	const riskScore = clamp(Math.round(rawRisk + (100 - store.complianceScore) * 0.25), 4, 96);
	const risk = riskFromScore(100 - riskScore);

	return {
		id: `an-${Date.now().toString(36)}`,
		storeId: store.id,
		storeName: store.name,
		storeCode: store.code,
		createdAt: Date.now(),
		imageLabel,
		riskScore,
		risk,
		detections,
		headline: headlineFor(detections, store),
		narrative: narrativeFor(detections, store, riskScore),
		frameCount: randInt(1, 4),
		modelVersion: MODEL_VERSION,
	};
}

function headlineFor(dets: Detection[], store: Store): string {
	if (!dets.length) return `No violations detected at ${store.name} — store is within standard.`;
	const crit = dets.filter((d) => d.severity === 'critical').length;
	const maj = dets.filter((d) => d.severity === 'major').length;
	if (crit) return `${crit} critical finding${crit > 1 ? 's' : ''} at ${store.name} need same-day action.`;
	if (maj) return `${maj} major finding${maj > 1 ? 's' : ''} at ${store.name} to correct this week.`;
	return `${dets.length} minor finding${dets.length > 1 ? 's' : ''} logged at ${store.name}.`;
}

function narrativeFor(dets: Detection[], store: Store, riskScore: number): string {
	if (!dets.length) {
		return `The model reviewed the upload against all five brand-standard areas and found no non-conformances. ${store.name} continues to track above the network average — keep the current routine in place.`;
	}
	const cats = Array.from(new Set(dets.map((d) => d.category)));
	const worst = dets.slice().sort((a, b) => SEVERITY_WEIGHT[b.severity] - SEVERITY_WEIGHT[a.severity])[0];
	const band = riskFromScore(100 - riskScore);
	const bandLine =
		band === 'critical'
			? 'This places the store in the severe band; manager intervention is required today.'
			: band === 'high'
				? 'This lifts the store into the high-risk band; a re-inspection within 72 hours is advised.'
				: band === 'medium'
					? 'The store sits in the moderate band; corrective actions should close within the week.'
					: 'Overall exposure stays low; address the items at the next routine visit.';
	return `The model surfaced ${dets.length} finding${dets.length > 1 ? 's' : ''} spanning ${cats.length} area${
		cats.length > 1 ? 's' : ''
	} (${cats.join(', ')}). The most significant is "${worst.label}" at ${Math.round(
		worst.confidence * 100,
	)}% confidence. ${bandLine}`;
}

/** Async wrapper — mimics a round-trip to a vision service. */
export async function analyzeInspection(
	store: Store,
	imageLabel?: string,
): Promise<AnalysisResult> {
	await delay(2600, 500);
	return composeAnalysis(store, imageLabel);
}

// --- Report composition --------------------------------------------------------

function recommendationsFor(dets: Detection[], store: Store): Recommendation[] {
	if (!dets.length) {
		return [
			{
				id: 'rec-hold',
				title: 'Maintain current routine',
				detail: `${store.name} is clear this cycle. Keep the mid-shift checks and daily temperature logs running.`,
				priority: 'monitor',
				owner: store.manager,
				icon: 'check-circle',
			},
			{
				id: 'rec-share',
				title: 'Share the win',
				detail: 'Feature this store in the regional standup as a reference for prep-zone discipline.',
				priority: 'monitor',
				owner: 'Area Manager',
				icon: 'award',
			},
		];
	}
	const bySeverity = dets.slice().sort((a, b) => SEVERITY_WEIGHT[b.severity] - SEVERITY_WEIGHT[a.severity]);
	const recs: Recommendation[] = bySeverity.slice(0, 4).map((d, i) => ({
		id: `rec-${d.id}-${i}`,
		title: d.remediation.split('.')[0].trim(),
		detail: `${d.label} · ${d.standardRef}. ${d.remediation}`,
		priority: d.severity === 'critical' ? 'now' : d.severity === 'major' ? 'soon' : 'monitor',
		owner: i === 0 ? store.manager : pick([store.manager, 'Shift Lead', 'Area Manager']),
		icon: d.icon,
	}));
	if (dets.some((d) => d.severity === 'critical')) {
		recs.push({
			id: 'rec-reinspect',
			title: 'Book a 72-hour re-inspection',
			detail: 'Schedule an AI photo re-check to confirm the critical items are closed.',
			priority: 'now',
			owner: 'Area Manager',
			icon: 'refresh',
		});
	}
	return recs;
}

function timelineFor(analysis: AnalysisResult, store: Store): TimelineEvent[] {
	const base: TimelineEvent[] = [
		{
			id: 't-upload',
			time: 'T-0',
			title: 'Evidence uploaded',
			detail: `${analysis.frameCount} frame${analysis.frameCount > 1 ? 's' : ''} from ${analysis.imageLabel}.`,
			icon: 'camera',
			tone: 'info',
		},
		{
			id: 't-scan',
			time: '+18s',
			title: 'Vision model completed',
			detail: `${analysis.detections.length} finding${
				analysis.detections.length === 1 ? '' : 's'
			} · model ${analysis.modelVersion}.`,
			icon: 'brain',
			tone: 'violet',
		},
	];
	if (analysis.detections.some((d) => d.severity === 'critical')) {
		base.push({
			id: 't-alert',
			time: '+20s',
			title: 'Critical alert raised',
			detail: `Pushed to ${store.manager} and the Area Manager queue.`,
			icon: 'bell',
			tone: 'risk',
		});
	}
	base.push({
		id: 't-report',
		time: '+34s',
		title: 'Compliance report generated',
		detail: 'Ready to download or share with the franchisee.',
		icon: 'file-text',
		tone: 'good',
	});
	return base;
}

const SWATCHES: Array<[string, string]> = [
	['#1f5bff', '#7c5cff'],
	['#12b5a6', '#1f5bff'],
	['#e08404', '#e23b2f'],
	['#7c5cff', '#4636d9'],
	['#12a05f', '#12b5a6'],
];

function evidenceFor(dets: Detection[]): EvidenceShot[] {
	if (!dets.length) {
		return [
			{
				id: 'ev-clean-1',
				label: 'Prep line — clear',
				severity: 'minor',
				swatch: SWATCHES[4],
				tags: ['Reference', 'Pass'],
			},
			{
				id: 'ev-clean-2',
				label: 'Cold well — in range',
				severity: 'minor',
				swatch: SWATCHES[1],
				tags: ['3°C', 'Pass'],
			},
		];
	}
	return dets.map((d, i) => ({
		id: `ev-${d.id}`,
		label: d.label,
		severity: d.severity,
		swatch: SWATCHES[i % SWATCHES.length],
		tags: [d.category, `${Math.round(d.confidence * 100)}%`],
	}));
}

/** Turn an analysis into a full report (synchronous). */
export function composeReport(
	analysis: AnalysisResult,
	store: Store,
	inspector: string,
): ComplianceReport {
	const counts: Record<Severity, number> = { minor: 0, major: 0, critical: 0 };
	analysis.detections.forEach((d) => {
		counts[d.severity] += 1;
	});
	const complianceEquivalent = clamp(100 - analysis.riskScore, 8, 99);

	return {
		id: `rep-${analysis.id}`,
		ref: makeRef('FG-REP'),
		storeId: store.id,
		storeName: store.name,
		storeCode: store.code,
		generatedAt: Date.now(),
		riskScore: analysis.riskScore,
		risk: analysis.risk,
		grade: scoreGrade(complianceEquivalent),
		counts,
		summary: analysis.narrative,
		detections: analysis.detections,
		recommendations: recommendationsFor(analysis.detections, store),
		timeline: timelineFor(analysis, store),
		evidence: evidenceFor(analysis.detections),
		inspector,
		modelVersion: analysis.modelVersion,
	};
}

/** Async wrapper for the "Generate report" action. */
export async function generateReport(
	analysis: AnalysisResult,
	store: Store,
	inspector: string,
): Promise<ComplianceReport> {
	await delay(2000, 400);
	return composeReport(analysis, store, inspector);
}

/** Occasionally used to make counters wobble like live data. */
export function liveWobble(base: number, spread = 1): number {
	return chance(0.5) ? base : round(base + jitter(0, spread));
}
