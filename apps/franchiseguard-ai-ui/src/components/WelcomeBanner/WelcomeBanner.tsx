// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { getGreeting } from '../../utils/greeting';
import { cx } from '../../utils/cx';
import styles from './WelcomeBanner.module.css';

export interface WelcomeBannerProps {
	name: string;
	/** Small label above the greeting. Defaults to today's date. */
	eyebrow?: string;
	subtitle?: string;
	className?: string;
	style?: React.CSSProperties;
}

const formatToday = (): string =>
	new Date().toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' });

/** "Good Morning, Area Manager" with a date eyebrow and an optional briefing. */
export const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
	name,
	eyebrow,
	subtitle,
	className,
	style,
}) => (
	<header className={cx(styles.wrap, className)} style={style}>
		<p className={styles.eyebrow}>{eyebrow ?? formatToday()}</p>
		<h1 className={styles.title}>
			{getGreeting()}, {name}
		</h1>
		{subtitle && <p className={styles.sub}>{subtitle}</p>}
	</header>
);
