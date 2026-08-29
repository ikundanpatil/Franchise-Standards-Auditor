// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useState } from 'react';
import { Icon } from '../../components/Icon/Icon';
import { Button } from '../../components/primitives/Button';
import { TextField } from '../../components/primitives/Field';
import { Divider } from '../../components/primitives/Misc';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { MANAGER } from '../../data/manager';
import styles from './Login.module.css';

export const Login: React.FC = () => {
	const nav = useNav();
	const { flash } = useToast();
	const [email, setEmail] = useState(MANAGER.email);
	const [password, setPassword] = useState('••••••••••');
	const [busy, setBusy] = useState<null | 'sso' | 'bio'>(null);

	const go = (mode: 'sso' | 'bio') => {
		setBusy(mode);
		flash(mode === 'bio' ? 'Verifying biometrics…' : 'Signing in with RocketRide…', 'fingerprint');
		setTimeout(() => nav.replace('home'), 1150);
	};

	return (
		<div className={styles.wrap}>
			<div className={styles.hero}>
				<div className={styles.brandRow}>
					<span className={styles.mark}>
						<Icon name="shield-check" size={20} />
					</span>
					<span className={styles.brand}>
						FranchiseGuard<b>AI</b>
					</span>
				</div>
				<h1 className={styles.title}>Welcome back, Area Manager</h1>
				<p className={styles.sub}>
					Sign in to review overnight AI inspections and triage risk across your {MANAGER.storesOwned}
					-store network.
				</p>
			</div>

			<div className={styles.card}>
				<TextField
					label="Work email"
					icon="mail"
					type="email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					autoComplete="username"
				/>
				<TextField
					label="Password"
					icon="lock"
					type="password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					autoComplete="current-password"
				/>
				<button type="button" className={styles.forgot} onClick={() => flash('Recovery link sent to your email.')}>
					Forgot password?
				</button>

				<Button
					variant="primary"
					size="lg"
					block
					icon="shield-check"
					loading={busy === 'sso'}
					onClick={() => go('sso')}
				>
					Continue with RocketRide
				</Button>

				<Divider label="or" />

				<Button
					variant="ghost"
					size="lg"
					block
					icon="fingerprint"
					loading={busy === 'bio'}
					onClick={() => go('bio')}
				>
					Use biometric login
				</Button>
			</div>

			<div className={styles.enterprise}>
				<span className={styles.lock}>
					<Icon name="lock" size={12} />
				</span>
				<span>
					<b>Enterprise SSO</b> · SOC 2 Type II · data stays in your brand's tenant
				</span>
			</div>
		</div>
	);
};
