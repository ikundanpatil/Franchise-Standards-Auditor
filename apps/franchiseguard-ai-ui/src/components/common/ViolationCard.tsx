// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { SeverityChip } from '../primitives/Chip';
import { cx } from '../../utils/cx';
import { SEVERITY_TONE } from '../../utils/risk';
import type { Detection } from '../../types';
import styles from './ViolationCard.module.css';

export interface ViolationCardProps {
	detection: Detection;
	expanded?: boolean;
	onToggle?: () => void;
	active?: boolean;
	className?: string;
	style?: React.CSSProperties;
}

/** Expandable AI finding — confidence bar, severity chip, model rationale. */
export const ViolationCard: React.FC<ViolationCardProps> = ({
	detection: d,
	expanded,
	onToggle,
	active,
	className,
	style,
}) => (
	<div
		className={cx(styles.card, active && styles.active, className)}
		style={style}
		data-fg-tone={SEVERITY_TONE[d.severity]}
	>
		<button type="button" className={styles.head} onClick={onToggle} aria-expanded={expanded}>
			<span className={styles.glyph}>
				<Icon name={d.icon} size={18} />
			</span>
			<span className={styles.headBody}>
				<span className={styles.title}>{d.label}</span>
				<span className={styles.cat}>{d.category}</span>
			</span>
			<span className={styles.right}>
				<SeverityChip severity={d.severity} />
				<Icon name="chevron-down" size={16} className={cx(styles.chev, expanded && styles.chevOpen)} />
			</span>
		</button>

		<div className={styles.confRow}>
			<span className={styles.confLabel}>AI confidence</span>
			<span className={styles.confTrack}>
				<span className={styles.confFill} style={{ width: `${Math.round(d.confidence * 100)}%` }} />
			</span>
			<b className={styles.confVal}>{Math.round(d.confidence * 100)}%</b>
		</div>

		{expanded && (
			<div className={styles.detail}>
				<p className={styles.explain}>{d.explanation}</p>
				<div className={styles.kv}>
					<span>
						<Icon name="file-text" size={12} /> {d.standardRef}
					</span>
					<span>
						<Icon name="target" size={12} /> {d.remediation}
					</span>
				</div>
			</div>
		)}
	</div>
);
