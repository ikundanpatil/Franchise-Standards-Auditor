// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { TimelineEvent } from '../../types';
import styles from './TimelineList.module.css';

export const TimelineList: React.FC<{ events: TimelineEvent[]; className?: string }> = ({
	events,
	className,
}) => (
	<ol className={cx(styles.list, className)}>
		{events.map((e, i) => (
			<li
				key={e.id}
				className={styles.item}
				data-fg-tone={e.tone}
				style={{ animationDelay: `${i * 70}ms` }}
			>
				<span className={styles.rail}>
					<span className={styles.node}>
						<Icon name={e.icon} size={13} />
					</span>
				</span>
				<span className={styles.body}>
					<span className={styles.time}>{e.time}</span>
					<span className={styles.title}>{e.title}</span>
					<span className={styles.detail}>{e.detail}</span>
				</span>
			</li>
		))}
	</ol>
);
