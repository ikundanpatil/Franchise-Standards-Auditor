// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { Sparkline } from '../Sparkline/Sparkline';
import { cx } from '../../utils/cx';
import type { StatItem } from '../../types';
import styles from './StatCard.module.css';

export type StatCardProps = Omit<StatItem, 'id'> & {
	className?: string;
	style?: React.CSSProperties;
};

const ARROW: Record<'up' | 'down' | 'flat', string> = { up: '▲', down: '▼', flat: '→' };

/** One KPI tile: tinted glyph, headline number, label and an optional trend. */
export const StatCard: React.FC<StatCardProps> = ({
	label,
	value,
	unit,
	caption,
	delta,
	tone,
	icon,
	trend,
	className,
	style,
}) => (
	<article className={cx(styles.card, className)} style={style} data-fg-tone={tone}>
		<div className={styles.top}>
			<span className={styles.icon} aria-hidden="true">
				<Icon name={icon} size={18} />
			</span>
			{trend && trend.length > 1 && <Sparkline data={trend} className={styles.spark} />}
		</div>

		<p className={styles.value}>
			{value}
			{unit && <span className={styles.unit}>{unit}</span>}
		</p>

		<p className={styles.label}>{label}</p>

		{(delta || caption) && (
			<p className={styles.meta}>
				{delta && (
					<span className={styles.delta}>
						{ARROW[delta.direction]} {delta.label}
					</span>
				)}
				{caption && <span className={styles.caption}>{caption}</span>}
			</p>
		)}
	</article>
);
