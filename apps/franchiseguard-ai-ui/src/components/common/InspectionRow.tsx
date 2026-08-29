// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import { shortDate, clockTime } from '../../lib/format';
import type { IconName, InspectionRecord } from '../../types';
import styles from './InspectionRow.module.css';

const STATUS: Record<InspectionRecord['status'], { label: string; tone: string; icon: IconName }> = {
	passed: { label: 'Passed', tone: 'good', icon: 'check-circle' },
	flagged: { label: 'Flagged', tone: 'warn', icon: 'alert-triangle' },
	failed: { label: 'Failed', tone: 'critical', icon: 'alert-octagon' },
	scheduled: { label: 'Scheduled', tone: 'info', icon: 'calendar' },
};

const METHOD: Record<InspectionRecord['method'], string> = {
	'ai-photo': 'AI · Photo',
	'ai-video': 'AI · Video',
	'on-site': 'On-site',
};

export const InspectionRow: React.FC<{
	record: InspectionRecord;
	onClick?: () => void;
	className?: string;
	style?: React.CSSProperties;
}> = ({ record, onClick, className, style }) => {
	const s = STATUS[record.status];
	return (
		<button
			type="button"
			className={cx(styles.row, className)}
			style={style}
			onClick={onClick}
			data-fg-tone={s.tone}
		>
			<span className={styles.icon}>
				<Icon name={s.icon} size={17} />
			</span>
			<span className={styles.body}>
				<span className={styles.top}>
					<span className={styles.store}>{record.storeName}</span>
					<span className={styles.code}>{record.storeCode}</span>
				</span>
				<span className={styles.summary}>{record.summary}</span>
				<span className={styles.meta}>
					{shortDate(record.date)} · {clockTime(record.date)} · {METHOD[record.method]} · {record.inspector}
				</span>
			</span>
			<span className={styles.right}>
				{record.status !== 'scheduled' ? (
					<b className={styles.score}>{record.score}</b>
				) : (
					<Icon name="clock" size={16} className={styles.pending} />
				)}
				<span className={styles.status}>{s.label}</span>
			</span>
		</button>
	);
};
