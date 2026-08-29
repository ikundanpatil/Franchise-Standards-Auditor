// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useEffect } from 'react';
import { Icon } from '../Icon/Icon';
import styles from './Sheet.module.css';

export interface SheetProps {
	open: boolean;
	onClose: () => void;
	title?: string;
	children: React.ReactNode;
	/** Optional sticky footer, e.g. action buttons. */
	footer?: React.ReactNode;
}

/** Bottom sheet with a scrim. Mounts only while open. */
export const Sheet: React.FC<SheetProps> = ({ open, onClose, title, children, footer }) => {
	useEffect(() => {
		if (!open) return;
		const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
		document.addEventListener('keydown', onKey);
		return () => document.removeEventListener('keydown', onKey);
	}, [open, onClose]);

	if (!open) return null;

	return (
		<div className={styles.root} role="dialog" aria-modal="true" aria-label={title}>
			<div className={styles.scrim} onClick={onClose} />
			<div className={styles.panel}>
				<div className={styles.grip} aria-hidden="true" />
				{title && (
					<header className={styles.head}>
						<h3 className={styles.title}>{title}</h3>
						<button type="button" className={styles.close} onClick={onClose} aria-label="Close">
							<Icon name="x" size={18} />
						</button>
					</header>
				)}
				<div className={styles.body}>{children}</div>
				{footer && <footer className={styles.foot}>{footer}</footer>}
			</div>
		</div>
	);
};
