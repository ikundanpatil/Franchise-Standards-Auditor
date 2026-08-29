// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import { CHECKLIST } from '../../data/checklist';
import styles from './ChecklistGroup.module.css';

export interface ChecklistGroupProps {
	/** Set of checked item ids. */
	checked: Set<string>;
	onToggle: (id: string) => void;
	className?: string;
}

/** The five brand-standard checks, each a tappable row. */
export const ChecklistGroup: React.FC<ChecklistGroupProps> = ({ checked, onToggle, className }) => (
	<ul className={cx(styles.list, className)}>
		{CHECKLIST.map((item) => {
			const on = checked.has(item.id);
			return (
				<li key={item.id}>
					<button
						type="button"
						className={cx(styles.row, on && styles.on)}
						onClick={() => onToggle(item.id)}
						aria-pressed={on}
					>
						<span className={styles.glyph}>
							<Icon name={item.icon} size={17} />
						</span>
						<span className={styles.body}>
							<span className={styles.label}>{item.label}</span>
							<span className={styles.hint}>{item.hint}</span>
						</span>
						<span className={styles.check} aria-hidden="true">
							{on && <Icon name="check" size={13} />}
						</span>
					</button>
				</li>
			);
		})}
	</ul>
);
