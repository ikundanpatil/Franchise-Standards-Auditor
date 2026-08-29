// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import { RISK_LABEL, RISK_TONE } from '../../utils/risk';
import type { RiskLevel } from '../../types';
import styles from './RiskBadge.module.css';

export interface RiskBadgeProps {
	level: RiskLevel;
	className?: string;
}

/** Pill that encodes severity in both colour and, for Critical, a solid fill. */
export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, className }) => (
	<span
		className={cx(styles.badge, level === 'critical' && styles.solid, className)}
		data-fg-tone={RISK_TONE[level]}
	>
		<span className={styles.dot} aria-hidden="true" />
		{RISK_LABEL[level]}
	</span>
);
