// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import { SEVERITY_LABEL, SEVERITY_TONE } from '../../utils/risk';
import type { IconName, Severity } from '../../types';
import styles from './Chip.module.css';

export interface ChipProps {
	label: string;
	tone?: string;
	icon?: IconName;
	solid?: boolean;
	className?: string;
}

/** Small status pill; `tone` picks the semantic colour pair. */
export const Chip: React.FC<ChipProps> = ({ label, tone = 'info', icon, solid, className }) => (
	<span
		className={cx(styles.chip, solid && styles.solid, className)}
		data-fg-tone={tone}
	>
		{icon && <Icon name={icon} size={11} />}
		{label}
	</span>
);

/** Severity chip used by the analysis + report screens. */
export const SeverityChip: React.FC<{ severity: Severity; className?: string }> = ({
	severity,
	className,
}) => (
	<Chip
		label={SEVERITY_LABEL[severity]}
		tone={SEVERITY_TONE[severity]}
		icon={severity === 'critical' ? 'alert-octagon' : severity === 'major' ? 'alert-triangle' : 'flag'}
		solid={severity === 'critical'}
		className={className}
	/>
);
