// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * App root: mounts the design tokens, the navigator and the toast host, then
 * renders the current screen inside a phone frame with a directional page
 * transition. Chrome (app header + bottom nav) is drawn by the shell so it
 * stays put while screens animate.
 */

import React, { useEffect } from 'react';
import { AppHeader } from '../components/AppHeader/AppHeader';
import { BottomNav } from '../components/BottomNav/BottomNav';
import { ensureFonts } from '../styles/fonts';
import { NavProvider, useNav } from './navigation';
import { ToastProvider } from './ToastHost';
import { CHROME_SCREENS, TABS, type TabId } from './routes';
import { SCREENS } from '../screens/registry';
import styles from './FranchiseGuardApp.module.css';
import '../styles/tokens.css';

const AppShell: React.FC<{ managerName: string }> = ({ managerName }) => {
	const nav = useNav();
	const ScreenComp = SCREENS[nav.screen];
	const withChrome = CHROME_SCREENS.has(nav.screen);

	const dirClass =
		nav.dir === 'forward' ? styles.enterR : nav.dir === 'back' ? styles.enterL : styles.enterFade;

	return (
		<div className={styles.frame}>
			{withChrome && (
				<AppHeader
					unreadCount={4}
					onNotificationsClick={() => nav.navigate('alerts')}
				/>
			)}

			<div className={styles.stage}>
				<div key={nav.entryKey} className={`${styles.page} ${dirClass}`}>
					<ScreenComp managerName={managerName} />
				</div>
			</div>

			{withChrome && (
				<BottomNav
					items={TABS}
					activeId={nav.activeTab ?? 'home'}
					onChange={(id) => nav.switchTab(id as TabId)}
				/>
			)}
		</div>
	);
};

export interface FranchiseGuardAppProps {
	managerName?: string;
}

export const FranchiseGuardApp: React.FC<FranchiseGuardAppProps> = ({
	managerName = 'Area Manager',
}) => {
	useEffect(() => {
		ensureFonts();
	}, []);

	return (
		<div className={styles.root} data-fg-root>
			<div className={styles.device}>
				<NavProvider initial="splash">
					<ToastProvider>
						<AppShell managerName={managerName} />
					</ToastProvider>
				</NavProvider>
			</div>
		</div>
	);
};

export default FranchiseGuardApp;
