// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { IconName } from '../../types';
import styles from './UploadCard.module.css';

export interface UploadCardProps {
	kind: 'camera' | 'gallery' | 'video';
	count: number;
	onAdd: () => void;
	className?: string;
	style?: React.CSSProperties;
}

const META: Record<UploadCardProps['kind'], { title: string; hint: string; icon: IconName }> = {
	camera: { title: 'Camera', hint: 'Capture on-site', icon: 'camera' },
	gallery: { title: 'Gallery', hint: 'Pick photos', icon: 'image' },
	video: { title: 'Walk-through', hint: 'Record video', icon: 'video' },
};

/** One capture source tile. Shows a filled state once evidence is attached. */
export const UploadCard: React.FC<UploadCardProps> = ({ kind, count, onAdd, className, style }) => {
	const meta = META[kind];
	const filled = count > 0;
	return (
		<button
			type="button"
			className={cx(styles.card, filled && styles.filled, className)}
			style={style}
			onClick={onAdd}
			data-fg-tone={kind === 'video' ? 'violet' : 'info'}
		>
			<span className={styles.icon}>
				<Icon name={filled ? 'check-circle' : meta.icon} size={20} />
			</span>
			<span className={styles.title}>{meta.title}</span>
			<span className={styles.hint}>{filled ? `${count} attached` : meta.hint}</span>
			{filled && (
				<span className={styles.thumbs} aria-hidden="true">
					{Array.from({ length: Math.min(count, 3) }).map((_, i) => (
						<span key={i} className={styles.thumb} data-i={i} />
					))}
				</span>
			)}
		</button>
	);
};
