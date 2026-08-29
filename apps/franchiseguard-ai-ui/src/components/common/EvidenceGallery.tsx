// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { SeverityChip } from '../primitives/Chip';
import { cx } from '../../utils/cx';
import type { EvidenceShot } from '../../types';
import styles from './EvidenceGallery.module.css';

/** Horizontal strip of evidence thumbnails (gradient placeholders + tags). */
export const EvidenceGallery: React.FC<{ shots: EvidenceShot[]; className?: string }> = ({
	shots,
	className,
}) => (
	<div className={cx(styles.scroller, className)}>
		{shots.map((s, i) => (
			<figure key={s.id} className={styles.shot} style={{ animationDelay: `${i * 60}ms` }}>
				<span
					className={styles.thumb}
					style={{ background: `linear-gradient(140deg, ${s.swatch[0]}, ${s.swatch[1]})` }}
				>
					<Icon name="eye" size={16} />
					<span className={styles.frameTag}>FRAME {String(i + 1).padStart(2, '0')}</span>
				</span>
				<figcaption className={styles.cap}>
					<span className={styles.capTitle}>{s.label}</span>
					<SeverityChip severity={s.severity} />
					<span className={styles.tags}>{s.tags.join(' · ')}</span>
				</figcaption>
			</figure>
		))}
	</div>
);
