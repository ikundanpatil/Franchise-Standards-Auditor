// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { useStepper } from '../../lib/hooks';
import type { IconName } from '../../types';
import styles from './LoadingOverlay.module.css';

export interface LoadingOverlayProps {
	steps: readonly string[];
	title?: string;
	icon?: IconName;
	/** ms per step — total ≈ stepMs * steps.length. */
	stepMs?: number;
	onDone?: () => void;
}

/** Full-panel "AI is working" overlay with a narrated step list. */
export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
	steps,
	title = 'Analyzing with FranchiseGuard AI',
	icon = 'brain',
	stepMs = 900,
	onDone,
}) => {
	const { index, progress, label } = useStepper(steps, stepMs, onDone);

	return (
		<div className={styles.root} role="status" aria-live="polite">
			<div className={styles.halo}>
				<span className={styles.ring} />
				<span className={styles.ring2} />
				<span className={styles.core}>
					<Icon name={icon} size={30} />
				</span>
			</div>

			<h2 className={styles.title}>{title}</h2>
			<p className={styles.now}>{label}</p>

			<div className={styles.track}>
				<span className={styles.fill} style={{ width: `${Math.max(6, progress * 100)}%` }} />
			</div>

			<ul className={styles.steps}>
				{steps.map((s, i) => (
					<li
						key={s}
						className={
							i < index ? styles.done : i === index ? styles.active : styles.pending
						}
					>
						<span className={styles.dot}>
							{i < index ? <Icon name="check" size={11} /> : i === index ? <span className={styles.spin} /> : null}
						</span>
						{s}
					</li>
				))}
			</ul>

			<p className={styles.foot}>Model fg-vision-2.4 · on-device pre-processing · encrypted upload</p>
		</div>
	);
};
