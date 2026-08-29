// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { Icon } from '../Icon/Icon';
import { Sparkline } from '../Sparkline/Sparkline';
import { RiskBadge } from '../RiskBadge/RiskBadge';
import { cx } from '../../utils/cx';
import { RISK_TONE } from '../../utils/risk';
import type { Store } from '../../types';
import styles from './StoreRow.module.css';

export const StoreRow: React.FC<{
	store: Store;
	onClick?: () => void;
	className?: string;
	style?: React.CSSProperties;
}> = ({ store, onClick, className, style }) => (
	<button
		type="button"
		className={cx(styles.row, className)}
		style={style}
		onClick={onClick}
		data-fg-tone={RISK_TONE[store.risk]}
	>
		<span className={styles.badge}>{store.complianceScore}</span>
		<span className={styles.main}>
			<span className={styles.name}>{store.name}</span>
			<span className={styles.meta}>
				{store.code} · {store.region}
				{store.openViolations > 0 && (
					<span className={styles.open}>· {store.openViolations} open</span>
				)}
			</span>
			<span className={styles.foot}>
				<RiskBadge level={store.risk} />
				<Sparkline data={store.trend} className={styles.spark} />
			</span>
		</span>
		<Icon name="chevron-right" size={17} className={styles.chev} />
	</button>
);
