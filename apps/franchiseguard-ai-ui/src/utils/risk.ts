// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import type { RiskLevel, Severity, Tone } from '../types';

/** Display label for each severity. */
export const RISK_LABEL: Record<RiskLevel, string> = {
	low: 'Low Risk',
	medium: 'Medium Risk',
	high: 'High Risk',
	critical: 'Critical',
};

/** Maps a severity onto a `data-fg-tone` colour role (see `styles/tokens.css`). */
export const RISK_TONE: Record<RiskLevel, string> = {
	low: 'good',
	medium: 'warn',
	high: 'risk',
	critical: 'critical',
};

/** Short label for a report severity bucket. */
export const SEVERITY_LABEL: Record<Severity, string> = {
	minor: 'Minor',
	major: 'Major',
	critical: 'Critical',
};

/** Colour role for a report severity bucket. */
export const SEVERITY_TONE: Record<Severity, string> = {
	minor: 'warn',
	major: 'risk',
	critical: 'critical',
};

/** Weight used to roll severities up into a single risk score. */
export const SEVERITY_WEIGHT: Record<Severity, number> = {
	minor: 6,
	major: 15,
	critical: 28,
};

/** Bucket a 0–100 compliance score into a risk level. */
export function riskFromScore(score: number): RiskLevel {
	if (score >= 88) return 'low';
	if (score >= 75) return 'medium';
	if (score >= 60) return 'high';
	return 'critical';
}

/** Map a 0–100 score onto a CSS colour var for gauges / meters. */
export function scoreToneVar(score: number): string {
	const level = riskFromScore(score);
	const map: Record<RiskLevel, string> = {
		low: 'var(--fg-good)',
		medium: 'var(--fg-warn)',
		high: 'var(--fg-risk)',
		critical: 'var(--fg-critical)',
	};
	return map[level];
}

/** Letter grade for a compliance score. */
export function scoreGrade(score: number): string {
	if (score >= 93) return 'A';
	if (score >= 88) return 'A−';
	if (score >= 82) return 'B+';
	if (score >= 76) return 'B';
	if (score >= 70) return 'C+';
	if (score >= 63) return 'C';
	return 'D';
}

/** Colour role for an arbitrary tone value, defaulting sensibly. */
export const TONE_VALUES: Tone[] = ['good', 'risk', 'warn', 'info', 'violet'];
