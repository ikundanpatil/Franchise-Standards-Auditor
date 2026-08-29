// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { RiskBadge } from '../RiskBadge/RiskBadge';
import { cx } from '../../utils/cx';
import { RISK_TONE } from '../../utils/risk';
import type { AlertItem } from '../../types';
import styles from './AlertCard.module.css';

export type AlertCardProps = Omit<AlertItem, 'id'> & {
	onClick?: () => void;
	className?: string;
};

/** A single Recent Alerts row — severity stripe, glyph, meta and a chevron. */
export const AlertCard: React.FC<AlertCardProps> = ({
	title,
	location,
	timeAgo,
	level,
	icon,
	aiFlagged,
	onClick,
	className,
}) => (
	<button
		type="button"
		className={cx(styles.card, className)}
		data-fg-tone={RISK_TONE[level]}
		onClick={onClick}
	>
		<span className={styles.icon} aria-hidden="true">
			<Icon name={icon} size={19} />
		</span>

		<span className={styles.body}>
			<span className={styles.title}>
				{title}
				{aiFlagged && (
					<span className={styles.ai} title="Flagged by AI vision" aria-label="Flagged by AI vision">
						<Icon name="sparkle" size={9} />
					</span>
				)}
			</span>
			<span className={styles.loc}>{location}</span>
			<span className={styles.foot}>
				<RiskBadge level={level} />
				<span className={styles.time}>{timeAgo}</span>
			</span>
		</span>

		<Icon name="chevron-right" size={18} className={styles.chev} aria-hidden="true" />
	</button>
);
