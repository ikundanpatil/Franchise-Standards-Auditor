// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import type { NavItem } from '../../types';
import styles from './BottomNav.module.css';

export interface BottomNavProps {
	items: NavItem[];
	activeId: string;
	onChange: (id: string) => void;
}

/** Fixed bottom tab bar. Column count follows `items.length`. */
export const BottomNav: React.FC<BottomNavProps> = ({ items, activeId, onChange }) => (
	<nav className={styles.nav} aria-label="Primary">
		{items.map((item) => {
			const active = item.id === activeId;
			return (
				<button
					key={item.id}
					type="button"
					className={styles.tab}
					aria-current={active ? 'page' : undefined}
					onClick={() => onChange(item.id)}
				>
					<Icon name={item.icon} size={21} />
					<span className={styles.label}>{item.label}</span>
				</button>
			);
		})}
	</nav>
);
