// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { Recommendation } from '../../types';
import styles from './RecommendationCard.module.css';

const PRIORITY: Record<Recommendation['priority'], { label: string; tone: string }> = {
	now: { label: 'Do now', tone: 'critical' },
	soon: { label: 'This week', tone: 'warn' },
	monitor: { label: 'Monitor', tone: 'info' },
};

export const RecommendationCard: React.FC<{
	rec: Recommendation;
	className?: string;
	style?: React.CSSProperties;
}> = ({ rec, className, style }) => {
	const p = PRIORITY[rec.priority];
	return (
		<article className={cx(styles.card, className)} style={style} data-fg-tone={p.tone}>
			<span className={styles.glyph}>
				<Icon name={rec.icon} size={17} />
			</span>
			<div className={styles.body}>
				<div className={styles.top}>
					<h4 className={styles.title}>{rec.title}</h4>
					<span className={styles.pill}>{p.label}</span>
				</div>
				<p className={styles.detail}>{rec.detail}</p>
				<p className={styles.owner}>
					<Icon name="user" size={11} /> Owner · {rec.owner}
				</p>
			</div>
		</article>
	);
};
