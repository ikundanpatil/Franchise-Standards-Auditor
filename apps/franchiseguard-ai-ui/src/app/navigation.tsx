// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * A dependency-free stack navigator. One entry = one screen plus its params;
 * `navigate` pushes, `back` pops, tab taps reset to a tab root. Kept tiny on
 * purpose — the app is a linear demo flow, not a routed site.
 */

import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { SCREEN_TAB, TAB_ROOT, type NavParams, type ScreenName, type TabId } from './routes';

interface Entry {
	screen: ScreenName;
	params: NavParams;
	/** Direction hint for the page transition. */
	dir: 'forward' | 'back' | 'replace';
	key: number;
}

interface NavApi {
	screen: ScreenName;
	params: NavParams;
	dir: Entry['dir'];
	entryKey: number;
	depth: number;
	activeTab: TabId | null;
	canGoBack: boolean;
	navigate: (screen: ScreenName, params?: NavParams) => void;
	replace: (screen: ScreenName, params?: NavParams) => void;
	back: () => void;
	switchTab: (tab: TabId) => void;
	reset: (screen: ScreenName, params?: NavParams) => void;
}

const NavContext = createContext<NavApi | null>(null);

let seq = 1;
const makeEntry = (screen: ScreenName, params: NavParams, dir: Entry['dir']): Entry => ({
	screen,
	params,
	dir,
	key: seq++,
});

export const NavProvider: React.FC<{ initial?: ScreenName; children: React.ReactNode }> = ({
	initial = 'splash',
	children,
}) => {
	const [stack, setStack] = useState<Entry[]>(() => [makeEntry(initial, {}, 'replace')]);

	const navigate = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack((prev) => [...prev, makeEntry(screen, params, 'forward')]);
	}, []);

	const replace = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack((prev) => [...prev.slice(0, -1), makeEntry(screen, params, 'replace')]);
	}, []);

	const back = useCallback(() => {
		setStack((prev) => {
			if (prev.length <= 1) return prev;
			const next = prev.slice(0, -1);
			const top = next[next.length - 1];
			next[next.length - 1] = { ...top, dir: 'back', key: seq++ };
			return next;
		});
	}, []);

	const reset = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack([makeEntry(screen, params, 'replace')]);
	}, []);

	const switchTab = useCallback((tab: TabId) => {
		setStack((prev) => {
			const current = prev[prev.length - 1];
			const root = TAB_ROOT[tab];
			if (current.screen === root && prev.length === 1) return prev;
			return [makeEntry(root, {}, 'replace')];
		});
	}, []);

	const top = stack[stack.length - 1];

	const value = useMemo<NavApi>(
		() => ({
			screen: top.screen,
			params: top.params,
			dir: top.dir,
			entryKey: top.key,
			depth: stack.length,
			activeTab: SCREEN_TAB[top.screen],
			canGoBack: stack.length > 1,
			navigate,
			replace,
			back,
			switchTab,
			reset,
		}),
		[top, stack.length, navigate, replace, back, switchTab, reset],
	);

	return <NavContext.Provider value={value}>{children}</NavContext.Provider>;
};

export function useNav(): NavApi {
	const ctx = useContext(NavContext);
	if (!ctx) throw new Error('useNav must be used inside <NavProvider>');
	return ctx;
}
