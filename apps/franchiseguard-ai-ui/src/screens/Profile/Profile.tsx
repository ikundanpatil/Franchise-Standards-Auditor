// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Profile — the "Profile" tab: the signed-in Area Manager's identity, their
 * network stats, account details, notification preferences and session
 * actions (alerts, support, sign out).
 */

import React, { useState } from 'react';
import {
	Avatar,
	Button,
	Card,
	Divider,
	Icon,
	KeyValue,
	MetricPill,
	SectionHeader,
	Toggle,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { MANAGER } from '../../data/manager';
import { STORES } from '../../data/stores';
import styles from './Profile.module.css';

export const Profile: React.FC<{ managerName: string }> = ({ managerName }) => {
	const nav = useNav();
	const { flash } = useToast();
	const [push, setPush] = useState(true);
	const [digest, setDigest] = useState(true);
	const [bio, setBio] = useState(false);

	const name = managerName || MANAGER.name;
	const highRisk = STORES.filter((s) => s.risk === 'high' || s.risk === 'critical').length;

	return (
		<main className={styles.scroll}>
			<Card padding="lg" className={`${styles.hero} ${styles.reveal}`}>
				<Avatar initials={MANAGER.initials} size={64} />
				<div className={styles.who}>
					<h1 className={styles.name}>{name}</h1>
					<p className={styles.role}>{MANAGER.title}</p>
					<p className={styles.mail}>
						<Icon name="mail" size={11} /> {MANAGER.email}
					</p>
				</div>
			</Card>

			<section className={`${styles.metrics} ${styles.reveal}`} style={{ animationDelay: '60ms' }}>
				<MetricPill icon="storefront" value={MANAGER.storesOwned} label="stores owned" tone="violet" />
				<MetricPill
					icon="clipboard-check"
					value={MANAGER.inspectionsThisMonth}
					label="this month"
					tone="info"
				/>
				<MetricPill icon="clock" value={`${MANAGER.avgResponseHours}h`} label="avg response" tone="good" />
				<MetricPill icon="alert-triangle" value={highRisk} label="high-risk stores" tone="risk" />
			</section>

			<Card padding="lg" className={styles.reveal} style={{ animationDelay: '110ms' }}>
				<SectionHeader title="Account" />
				<KeyValue k="Region" v={MANAGER.region} icon="map-pin" />
				<Divider />
				<KeyValue k="Member since" v={MANAGER.memberSince} icon="calendar" />
				<Divider />
				<KeyValue k="Plan" v="Enterprise · SOC 2 Type II" icon="shield-check" />
			</Card>

			<Card padding="lg" className={styles.reveal} style={{ animationDelay: '150ms' }}>
				<SectionHeader title="Notifications" />
				<div className={styles.toggleRow}>
					<span className={styles.toggleText}>
						<b>Critical alert push</b>
						<i>Instant phone alert on a critical finding</i>
					</span>
					<Toggle
						checked={push}
						onChange={(v) => {
							setPush(v);
							flash(v ? 'Critical push notifications on.' : 'Critical push notifications off.', 'bell');
						}}
						label="Critical alert push"
					/>
				</div>
				<Divider />
				<div className={styles.toggleRow}>
					<span className={styles.toggleText}>
						<b>Weekly digest email</b>
						<i>Monday 07:00 — network compliance summary</i>
					</span>
					<Toggle checked={digest} onChange={setDigest} label="Weekly digest email" />
				</div>
				<Divider />
				<div className={styles.toggleRow}>
					<span className={styles.toggleText}>
						<b>Biometric unlock</b>
						<i>Face ID / fingerprint on app open</i>
					</span>
					<Toggle
						checked={bio}
						onChange={(v) => {
							setBio(v);
							flash(v ? 'Biometric unlock enabled.' : 'Biometric unlock disabled.', 'fingerprint');
						}}
						label="Biometric unlock"
					/>
				</div>
			</Card>

			<section className={`${styles.actions} ${styles.reveal}`} style={{ animationDelay: '190ms' }}>
				<Button variant="secondary" block icon="bell" onClick={() => nav.navigate('alerts')}>
					Manager alerts
				</Button>
				<Button variant="ghost" block icon="file-text" onClick={() => flash('Opening the help centre…')}>
					Help &amp; support
				</Button>
				<Button
					variant="danger"
					block
					icon="logout"
					onClick={() => {
						flash('Signed out.');
						nav.reset('login');
					}}
				>
					Sign out
				</Button>
			</section>

			<p className={styles.version}>FranchiseGuard AI · v0.1.0 · fg-vision 2.4</p>
		</main>
	);
};

export default Profile;
