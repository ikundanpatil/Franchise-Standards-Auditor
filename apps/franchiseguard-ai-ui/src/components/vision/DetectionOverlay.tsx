// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import { SEVERITY_TONE } from '../../utils/risk';
import type { Detection } from '../../types';
import styles from './DetectionOverlay.module.css';

export interface DetectionOverlayProps {
	detections: Detection[];
	/** Highlighted detection id; others dim. */
	activeId?: string | null;
	onSelect?: (id: string) => void;
	/** Stagger the box-in animation. */
	animate?: boolean;
}

/** Absolutely-positioned bounding boxes over a <VisionScene>. */
export const DetectionOverlay: React.FC<DetectionOverlayProps> = ({
	detections,
	activeId,
	onSelect,
	animate = true,
}) => (
	<>
		{detections.map((d, i) => {
			const [x, y, w, h] = d.box;
			const dim = activeId != null && activeId !== d.id;
			const flipLabel = y < 0.16;
			return (
				<button
					key={d.id}
					type="button"
					className={cx(
						styles.box,
						dim && styles.dim,
						activeId === d.id && styles.active,
						animate && styles.animIn,
					)}
					data-fg-tone={SEVERITY_TONE[d.severity]}
					style={{
						left: `${x * 100}%`,
						top: `${y * 100}%`,
						width: `${w * 100}%`,
						height: `${h * 100}%`,
						animationDelay: `${i * 140}ms`,
					}}
					onClick={() => onSelect?.(d.id)}
				>
					<span className={cx(styles.tag, flipLabel && styles.tagBelow)}>
						{d.label}
						<b>{Math.round(d.confidence * 100)}%</b>
					</span>
					<span className={cx(styles.tick, styles.t1)} />
					<span className={cx(styles.tick, styles.t2)} />
					<span className={cx(styles.tick, styles.t3)} />
					<span className={cx(styles.tick, styles.t4)} />
				</button>
			);
		})}
	</>
);
