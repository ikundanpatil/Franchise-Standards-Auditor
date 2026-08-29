// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import styles from './Toast.module.css';

export interface ToastProps {
	/** Current message, or `null` to hide. Stays mounted so it can animate out. */
	message: string | null;
}

/** Lightweight status pill anchored above the bottom navigation. */
export const Toast: React.FC<ToastProps> = ({ message }) => (
	<div className={cx(styles.toast, message && styles.show)} role="status" aria-live="polite">
		<Icon name="sparkle" size={13} />
		<span>{message}</span>
	</div>
);
