// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import styles from './SectionHeader.module.css';

export interface SectionHeaderProps {
	title: string;
	/** Optional count chip after the title. */
	count?: number;
	/** Optional trailing link, e.g. "View all". */
	action?: { label: string; onClick?: () => void };
}

/** Row heading used above list sections. */
export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, count, action }) => (
	<div className={styles.row}>
		<h2 className={styles.title}>
			{title}
			{typeof count === 'number' && <span className={styles.count}>{count}</span>}
		</h2>
		{action && (
			<button type="button" className={styles.action} onClick={action.onClick}>
				{action.label}
				<Icon name="chevron-right" size={15} />
			</button>
		)}
	</div>
);
