// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { IconName } from '../../types';
import styles from './PageHeader.module.css';

export interface PageHeaderProps {
	title: string;
	subtitle?: string;
	icon?: IconName;
	onBack?: () => void;
	/** Optional trailing action button. */
	action?: { icon: IconName; label: string; onClick: () => void };
	className?: string;
}

/** Sub-screen header: back chevron, title block, optional action. */
export const PageHeader: React.FC<PageHeaderProps> = ({
	title,
	subtitle,
	icon,
	onBack,
	action,
	className,
}) => (
	<header className={cx(styles.header, className)}>
		{onBack && (
			<button type="button" className={styles.back} onClick={onBack} aria-label="Back">
				<Icon name="chevron-left" size={20} />
			</button>
		)}
		<div className={styles.titles}>
			<h1 className={styles.title}>
				{icon && <Icon name={icon} size={16} className={styles.titleIcon} />}
				{title}
			</h1>
			{subtitle && <p className={styles.sub}>{subtitle}</p>}
		</div>
		{action && (
			<button type="button" className={styles.action} onClick={action.onClick} aria-label={action.label}>
				<Icon name={action.icon} size={18} />
			</button>
		)}
	</header>
);
