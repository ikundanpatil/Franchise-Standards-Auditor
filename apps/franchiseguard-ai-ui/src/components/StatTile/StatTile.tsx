// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { Sparkline } from '../Sparkline/Sparkline';
import { useCountUp } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import { group } from '../../lib/format';
import type { StatItem } from '../../types';
import styles from './StatTile.module.css';

export type StatTileProps = Omit<StatItem, 'id'> & {
	className?: string;
	style?: React.CSSProperties;
	onClick?: () => void;
	index?: number;
};

const ARROW: Record<'up' | 'down' | 'flat', string> = { up: '▲', down: '▼', flat: '—' };

/** Frosted-glass KPI tile with an animated counter + inline trend. */
export const StatTile: React.FC<StatTileProps> = ({
	label,
	value,
	unit,
	caption,
	delta,
	tone,
	icon,
	trend,
	countTo,
	decimals = 0,
	className,
	style,
	onClick,
	index = 0,
}) => {
	const numeric = typeof countTo === 'number' ? countTo : typeof value === 'number' ? value : null;
	const shown = useCountUp(numeric ?? 0, { decimals, duration: 1200, startDelay: index * 90 });
	const display = numeric == null ? value : decimals ? shown.toFixed(decimals) : group(shown);

	const deltaGood =
		delta && (delta.direction === 'flat'
			? null
			: delta.invert
				? delta.direction === 'down'
				: delta.direction === 'up');

	const Wrapper: React.ElementType = onClick ? 'button' : 'div';

	return (
		<Wrapper
			className={cx(styles.tile, onClick && styles.pressable, className)}
			style={style}
			data-fg-tone={tone}
			onClick={onClick}
			type={onClick ? 'button' : undefined}
		>
			<span className={styles.sheen} aria-hidden="true" />
			<div className={styles.top}>
				<span className={styles.icon} aria-hidden="true">
					<Icon name={icon} size={17} />
				</span>
				{trend && trend.length > 1 && <Sparkline data={trend} className={styles.spark} />}
			</div>

			<p className={styles.value}>
				{display}
				{unit && <span className={styles.unit}>{unit}</span>}
			</p>
			<p className={styles.label}>{label}</p>

			{(delta || caption) && (
				<p className={styles.meta}>
					{delta && (
						<span
							className={styles.delta}
							data-good={deltaGood == null ? undefined : deltaGood ? 'yes' : 'no'}
						>
							{ARROW[delta.direction]} {delta.label}
						</span>
					)}
					{caption && <span className={styles.caption}>{caption}</span>}
				</p>
			)}
		</Wrapper>
	);
};
