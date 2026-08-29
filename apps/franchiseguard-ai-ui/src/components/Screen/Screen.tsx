// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Screen.module.css';

export interface ScreenProps {
	/** Fixed area above the scroll region (header / page title). */
	header?: React.ReactNode;
	/** Sticky area below the scroll region (primary CTA). */
	footer?: React.ReactNode;
	children: React.ReactNode;
	className?: string;
	/** Extra bottom padding so content clears the app's bottom nav. */
	padForNav?: boolean;
}

/** Standard screen frame: fixed header, scrolling body, optional sticky footer. */
export const Screen: React.FC<ScreenProps> = ({
	header,
	footer,
	children,
	className,
	padForNav,
}) => (
	<div className={styles.screen}>
		{header}
		<main className={cx(styles.scroll, padForNav && styles.padNav, className)}>{children}</main>
		{footer && <div className={styles.footer}>{footer}</div>}
	</div>
);
