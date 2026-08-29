// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useEffect } from 'react';
import { Icon } from '../../components/Icon/Icon';
import { useNav } from '../../app/navigation';
import styles from './Splash.module.css';

/** Brand splash — animates in, then hands off to Login. */
export const Splash: React.FC = () => {
	const nav = useNav();

	useEffect(() => {
		const id = setTimeout(() => nav.replace('login'), 2600);
		return () => clearTimeout(id);
	}, [nav]);

	return (
		<button type="button" className={styles.wrap} onClick={() => nav.replace('login')} aria-label="Continue">
			<div className={styles.glow} aria-hidden="true" />

			<div className={styles.mark}>
				<span className={styles.ring} />
				<span className={styles.badge}>
					<Icon name="shield-check" size={40} />
				</span>
			</div>

			<h1 className={styles.wordmark}>
				FranchiseGuard<span>AI</span>
			</h1>
			<p className={styles.tag}>AI Compliance Intelligence for Franchise Operations</p>

			<div className={styles.loader} aria-hidden="true">
				<span />
				<span />
				<span />
			</div>

			<p className={styles.foot}>Powered by RocketRide · fg-vision 2.4</p>
		</button>
	);
};
