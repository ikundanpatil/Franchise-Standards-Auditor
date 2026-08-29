// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Shared domain + UI types for the FranchiseGuard AI client. */

/** Semantic colour role for stat tiles, badges and alert stripes. */
export type Tone = 'good' | 'risk' | 'warn' | 'info' | 'violet';

/** Severity of a compliance finding, worst-last. */
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

/** Severity buckets used in the compliance report. */
export type Severity = 'minor' | 'major' | 'critical';

/** Every glyph the app can draw — see `components/Icon`. */
export type IconName =
	| 'shield-check'
	| 'shield'
	| 'bell'
	| 'alert-triangle'
	| 'alert-octagon'
	| 'clipboard-clock'
	| 'clipboard-check'
	| 'storefront'
	| 'camera'
	| 'image'
	| 'video'
	| 'sparkle'
	| 'sparkles'
	| 'home'
	| 'clipboard-list'
	| 'chart'
	| 'chart-line'
	| 'user'
	| 'users'
	| 'chevron-right'
	| 'chevron-left'
	| 'chevron-down'
	| 'arrow-up-right'
	| 'droplet'
	| 'glove'
	| 'price-tag'
	| 'broom'
	| 'thermometer'
	| 'bug'
	| 'fingerprint'
	| 'mail'
	| 'lock'
	| 'check'
	| 'check-circle'
	| 'x'
	| 'x-circle'
	| 'clock'
	| 'calendar'
	| 'map-pin'
	| 'download'
	| 'share'
	| 'scale'
	| 'gavel'
	| 'flag'
	| 'refresh'
	| 'search'
	| 'filter'
	| 'plus'
	| 'settings'
	| 'logout'
	| 'trending-up'
	| 'trending-down'
	| 'target'
	| 'layers'
	| 'file-text'
	| 'brain'
	| 'eye'
	| 'zap'
	| 'star'
	| 'award'
	| 'chef-hat'
	| 'package'
	| 'wifi'
	| 'battery'
	| 'signal';

/** Movement indicator on a KPI. */
export interface Delta {
	label: string;
	direction: 'up' | 'down' | 'flat';
	/** When true, an "up" arrow is coloured as a regression (e.g. High Risk count). */
	invert?: boolean;
}

/** A single KPI shown in the dashboard stat grid. */
export interface StatItem {
	id: string;
	label: string;
	value: number | string;
	/** Suffix rendered small next to the value, e.g. `/100`. */
	unit?: string;
	/** Short qualifier under the value. */
	caption?: string;
	delta?: Delta;
	tone: Tone;
	icon: IconName;
	/** Optional series for the inline sparkline (oldest → newest). */
	trend?: number[];
	/** Numeric target used by the count-up animation (falls back to `value`). */
	countTo?: number;
	/** Decimal places for the animated counter. */
	decimals?: number;
}

/** A compliance issue surfaced in the Recent Alerts feed. */
export interface AlertItem {
	id: string;
	title: string;
	location: string;
	timeAgo: string;
	level: RiskLevel;
	icon: IconName;
	aiFlagged?: boolean;
}

/** A destination in the bottom navigation bar. */
export interface NavItem {
	id: string;
	label: string;
	icon: IconName;
}

/** Franchise store under an Area Manager's watch. */
export interface Store {
	id: string;
	code: string;
	name: string;
	region: string;
	address: string;
	manager: string;
	complianceScore: number;
	risk: RiskLevel;
	openViolations: number;
	lastInspection: string;
	nextInspectionDue: string;
	trend: number[];
	/** 90-day risk-score series, oldest → newest. */
	riskSeries: number[];
	openRate: number;
	tags: string[];
}

/** A completed or scheduled inspection record. */
export interface InspectionRecord {
	id: string;
	storeId: string;
	storeName: string;
	storeCode: string;
	date: string;
	inspector: string;
	score: number;
	risk: RiskLevel;
	violations: number;
	status: 'passed' | 'flagged' | 'failed' | 'scheduled';
	method: 'ai-photo' | 'ai-video' | 'on-site';
	summary: string;
}

/** Checklist row on the upload screen. */
export interface ChecklistItemDef {
	id: string;
	label: string;
	icon: IconName;
	hint: string;
}

/** Catalogue entry describing a class of violation the vision model can flag. */
export interface ViolationType {
	id: string;
	label: string;
	category: string;
	icon: IconName;
	severity: Severity;
	/** Normalised bounding box [x, y, w, h] in 0–1 image space. */
	box: [number, number, number, number];
	/** Template fragments the fake AI stitches into an explanation. */
	rationale: string;
	standardRef: string;
	remediation: string;
}

/** One detection produced by a (simulated) analysis run. */
export interface Detection {
	id: string;
	typeId: string;
	label: string;
	category: string;
	icon: IconName;
	severity: Severity;
	confidence: number;
	box: [number, number, number, number];
	explanation: string;
	standardRef: string;
	remediation: string;
}

/** Result of analysing an uploaded inspection. */
export interface AnalysisResult {
	id: string;
	storeId: string;
	storeName: string;
	storeCode: string;
	createdAt: number;
	imageLabel: string;
	riskScore: number;
	risk: RiskLevel;
	detections: Detection[];
	headline: string;
	narrative: string;
	frameCount: number;
	modelVersion: string;
}

/** A recommendation card in the compliance report. */
export interface Recommendation {
	id: string;
	title: string;
	detail: string;
	priority: 'now' | 'soon' | 'monitor';
	owner: string;
	icon: IconName;
}

/** A dated event in the report / location-memory timeline. */
export interface TimelineEvent {
	id: string;
	time: string;
	title: string;
	detail: string;
	icon: IconName;
	tone: Tone;
}

/** Piece of photographic evidence in the report gallery. */
export interface EvidenceShot {
	id: string;
	label: string;
	severity: Severity;
	/** Two hex stops for the placeholder thumbnail gradient. */
	swatch: [string, string];
	tags: string[];
}

/** A fully generated compliance report. */
export interface ComplianceReport {
	id: string;
	ref: string;
	storeId: string;
	storeName: string;
	storeCode: string;
	generatedAt: number;
	riskScore: number;
	risk: RiskLevel;
	grade: string;
	counts: Record<Severity, number>;
	summary: string;
	detections: Detection[];
	recommendations: Recommendation[];
	timeline: TimelineEvent[];
	evidence: EvidenceShot[];
	inspector: string;
	modelVersion: string;
}

/** Priority alert on the Manager Alerts screen. */
export interface ManagerAlert {
	id: string;
	title: string;
	storeName: string;
	storeCode: string;
	region: string;
	level: RiskLevel;
	category: string;
	icon: IconName;
	raisedAt: string;
	detail: string;
	aiConfidence: number;
	sla: string;
	status: 'open' | 'ack' | 'scheduled' | 'escalated';
}

/** Generic point for the chart primitives. */
export interface ChartPoint {
	label: string;
	value: number;
}

/** A named series for multi-series charts. */
export interface ChartSeries {
	name: string;
	color: string;
	points: number[];
}

/** Slice for the donut chart. */
export interface DonutSlice {
	label: string;
	value: number;
	color: string;
}

/** The signed-in Area Manager. */
export interface ManagerProfile {
	name: string;
	title: string;
	email: string;
	region: string;
	initials: string;
	memberSince: string;
	storesOwned: number;
	inspectionsThisMonth: number;
	avgResponseHours: number;
}
