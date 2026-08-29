// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import styles from './AppHeader.module.css';

export interface AppHeaderProps {
	/** Overrides the default "FranchiseGuard AI" wordmark. */
	title?: string;
	unreadCount?: number;
	onNotificationsClick?: () => void;
}

/** Sticky top bar: brand mark, wordmark and a notification bell. */
export const AppHeader: React.FC<AppHeaderProps> = ({
	title,
	unreadCount = 0,
	onNotificationsClick,
}) => (
	<header className={styles.header}>
		<div className={styles.brand}>
			<span className={styles.mark} aria-hidden="true">
				<Icon name="shield-check" size={20} />
			</span>
			{title ? (
				<span className={styles.name}>{title}</span>
			) : (
				<span className={styles.name}>
					FranchiseGuard<b>AI</b>
				</span>
			)}
		</div>

		<button
			type="button"
			className={styles.bell}
			onClick={onNotificationsClick}
			aria-label={unreadCount > 0 ? `Notifications, ${unreadCount} unread` : 'Notifications'}
		>
			<Icon name="bell" size={19} />
			{unreadCount > 0 && (
				<span className={styles.badge}>{unreadCount > 9 ? '9+' : unreadCount}</span>
			)}
		</button>
	</header>
);
