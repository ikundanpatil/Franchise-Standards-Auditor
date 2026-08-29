// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { useCountUp } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import { RISK_LABEL, riskFromScore } from '../../utils/risk';
import styles from './RiskMeter.module.css';

export interface RiskMeterProps {
	/** 0–100 risk score (higher = worse). */
	score: number;
	className?: string;
	compact?: boolean;
}

const BANDS = [
	{ upTo: 25, label: 'Low' },
	{ upTo: 50, label: 'Moderate' },
	{ upTo: 75, label: 'High' },
	{ upTo: 100, label: 'Severe' },
];

/** Horizontal gradient meter with a needle at `score`. */
export const RiskMeter: React.FC<RiskMeterProps> = ({ score, className, compact }) => {
	const clamped = Math.max(0, Math.min(100, score));
	const shown = useCountUp(clamped, { duration: 1000 });
	// Invert: gauge uses compliance-style risk bucketing on (100 - risk).
	const level = riskFromScore(100 - clamped);

	return (
		<div className={cx(styles.wrap, compact && styles.compact, className)}>
			<div className={styles.head}>
				<span className={styles.caption}>AI Risk Index</span>
				<span className={styles.score} data-fg-tone={
					level === 'low' ? 'good' : level === 'medium' ? 'warn' : level === 'high' ? 'risk' : 'critical'
				}>
					{Math.round(shown)}
					<i>/100</i>
				</span>
			</div>
			<div className={styles.track}>
				<span className={styles.fill} style={{ width: `${clamped}%` }} />
				<span className={styles.needle} style={{ left: `${clamped}%` }} aria-hidden="true" />
			</div>
			<div className={styles.bands}>
				{BANDS.map((b) => (
					<span key={b.label}>{b.label}</span>
				))}
			</div>
			{!compact && (
				<p className={styles.verdict}>
					Model verdict: <b>{RISK_LABEL[level]}</b> — {verdictLine(level)}
				</p>
			)}
		</div>
	);
};

function verdictLine(level: string): string {
	switch (level) {
		case 'low':
			return 'store is within brand standard tolerances.';
		case 'medium':
			return 'minor corrective actions recommended this week.';
		case 'high':
			return 'schedule a re-inspection within 72 hours.';
		default:
			return 'immediate manager intervention required.';
	}
}
