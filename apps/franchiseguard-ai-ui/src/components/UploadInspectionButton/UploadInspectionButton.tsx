// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import styles from './UploadInspectionButton.module.css';

export interface UploadInspectionButtonProps {
	label?: string;
	hint?: string;
	onClick?: () => void;
	className?: string;
	style?: React.CSSProperties;
}

/** Primary call to action — capture a photo for the vision model to score. */
export const UploadInspectionButton: React.FC<UploadInspectionButtonProps> = ({
	label = 'Upload Inspection',
	hint = 'Snap a photo of any store area — AI scores it instantly',
	onClick,
	className,
	style,
}) => (
	<button type="button" className={cx(styles.button, className)} style={style} onClick={onClick}>
		<span className={styles.icon} aria-hidden="true">
			<Icon name="camera" size={24} />
		</span>
		<span className={styles.body}>
			<span className={styles.label}>{label}</span>
			<span className={styles.hint}>{hint}</span>
		</span>
		<span className={styles.tag}>
			<span className={styles.pulse} aria-hidden="true" />
			AI
		</span>
	</button>
);
